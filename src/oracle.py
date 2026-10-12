"""Persistência Oracle real, binds e transações atômicas; sem banco substituto."""
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import os
import oracledb
from dotenv import load_dotenv
from .domain import Talhao, Colheita, identifier, harvest_date, number

ROOT = Path(__file__).resolve().parents[1]


def output_type_handler(cursor, metadata):
    if metadata.type_code == oracledb.DB_TYPE_NUMBER:
        return cursor.var(str, arraysize=cursor.arraysize, outconverter=Decimal)


def connect():
    load_dotenv(ROOT / '.env')
    values = [os.getenv(k) for k in ('APP_USER', 'APP_USER_PASSWORD', 'ORACLE_DSN')]
    if not all(values):
        raise ValueError('Configure APP_USER, APP_USER_PASSWORD e ORACLE_DSN no .env.')
    connection = oracledb.connect(user=values[0], password=values[1], dsn=values[2],
                                 tcp_connect_timeout=10)
    connection.call_timeout = 15000
    connection.outputtypehandler = output_type_handler
    return connection


def initialize(connection):
    """DDL fora das transações de dados: cria somente as tabelas ausentes."""
    with connection.cursor() as cursor:
        for sql in (ROOT / 'database/schema.sql').read_text(encoding='utf-8').split(';'):
            if sql.strip():
                try:
                    cursor.execute(sql.strip())
                except oracledb.DatabaseError as exc:
                    if exc.args[0].code != 955:
                        raise


@contextmanager
def transaction(connection):
    try:
        yield
        connection.commit()
    except BaseException:
        connection.rollback()
        raise


class Repository:
    def __init__(self, connection):
        self.connection = connection

    def talhoes(self):
        with self.connection.cursor() as c:
            c.execute('SELECT id, nome, area_ha FROM talhoes ORDER BY id')
            return [Talhao(*row) for row in c]

    def colheitas(self, talhao_id=None):
        sql = 'SELECT id, talhao_id, data, area_ha, producao_t, perda_kg_ha, preco_t FROM colheitas'
        params = {}
        if talhao_id is not None:
            params['id'] = identifier(talhao_id)
            sql += ' WHERE talhao_id = :id'
        with self.connection.cursor() as c:
            c.execute(sql + ' ORDER BY data, id', params)
            return [Colheita(row[0], row[1], row[2].date(), *row[3:]) for row in c]

    def snapshot(self):
        # Duas tabelas na mesma fotografia consistente do Oracle.
        with transaction(self.connection):
            with self.connection.cursor() as c:
                c.execute('SET TRANSACTION READ ONLY')
            return self.talhoes(), self.colheitas()

    def add_talhao(self, talhao):
        with transaction(self.connection):
            self._insert_talhao(talhao)

    def _insert_talhao(self, talhao):
        with self.connection.cursor() as c:
            c.execute('INSERT INTO talhoes (id, nome, area_ha) VALUES (:id, :nome, :area)',
                      id=talhao.id, nome=talhao.nome, area=talhao.area_ha)

    def edit_talhao(self, talhao):
        with transaction(self.connection):
            with self.connection.cursor() as c:
                c.execute('UPDATE talhoes SET nome=:nome, area_ha=:area WHERE id=:id',
                          nome=talhao.nome, area=talhao.area_ha, id=talhao.id)
                if c.rowcount == 0:
                    raise ValueError('Talhão inexistente.')

    def add_colheita(self, record_id, talhao_id, data, producao_t, perda_kg_ha, preco_t):
        identifier(talhao_id)
        with transaction(self.connection):
            with self.connection.cursor() as c:
                c.execute('SELECT area_ha FROM talhoes WHERE id=:id FOR UPDATE', id=talhao_id)
                row = c.fetchone()
                if row is None:
                    raise ValueError('Talhão inexistente. Cadastre-o primeiro.')
                record = Colheita(record_id, talhao_id, data, row[0], producao_t, perda_kg_ha, preco_t)
                self._insert_colheita(record)
        return record

    def _insert_colheita(self, record):
        with self.connection.cursor() as c:
            c.execute('''INSERT INTO colheitas
                      (id, talhao_id, data, area_ha, producao_t, perda_kg_ha, preco_t)
                      VALUES (:id, :talhao, :data, :area, :producao, :perda, :preco)''',
                      id=record.id, talhao=record.talhao_id,
                      data=datetime.combine(record.data, datetime.min.time()), area=record.area_ha,
                      producao=record.producao_t, perda=record.perda_kg_ha, preco=record.preco_t)

    def edit_colheita(self, record_id, data, producao_t, perda_kg_ha, preco_t):
        # Talhão e área histórica são imutáveis; corrige os dados observados.
        identifier(record_id)
        dt = harvest_date(data)
        production = number(producao_t, 'Produção')
        loss = number(perda_kg_ha, 'Perda')
        price = number(preco_t, 'Preço', positive=True)
        with transaction(self.connection):
            with self.connection.cursor() as c:
                c.execute('''UPDATE colheitas SET data=:data, producao_t=:producao,
                          perda_kg_ha=:perda, preco_t=:preco WHERE id=:id''',
                          data=datetime.combine(dt, datetime.min.time()), producao=production,
                          perda=loss, preco=price, id=record_id)
                if c.rowcount == 0:
                    raise ValueError('Colheita inexistente.')

    def delete(self, kind, record_id):
        identifier(record_id)
        queries = {'talhao': 'DELETE FROM talhoes WHERE id=:id',
                   'colheita': 'DELETE FROM colheitas WHERE id=:id'}
        if kind not in queries:
            raise ValueError('Tipo de registro inválido.')
        with transaction(self.connection):
            with self.connection.cursor() as c:
                c.execute(queries[kind], id=record_id)
                if c.rowcount == 0:
                    raise ValueError('Registro inexistente.')

    def import_data(self, talhoes, colheitas):
        # Revalidação na fronteira do repositório; não confiar no chamador.
        from dataclasses import asdict
        from .files import validate_payload
        talhoes, colheitas = validate_payload({'versao': 1,
            'talhoes': [asdict(t) for t in talhoes], 'colheitas': [asdict(c) for c in colheitas]})
        with transaction(self.connection):
            existing = {t.id: t for t in self.talhoes()}
            for t in talhoes:
                if t.id in existing:
                    if existing[t.id] != t:
                        raise ValueError(f'Talhão {t.id} já existe com dados diferentes. Nada importado.')
                else:
                    self._insert_talhao(t)
            for r in colheitas:
                self._insert_colheita(r)


def friendly_error(exc):
    if isinstance(exc, oracledb.Error):
        code = getattr(exc.args[0], 'code', None)
        return {1: 'Identificador duplicado ou colheita já registrada para esse talhão e data.',
                2292: 'O talhão possui colheitas. Exclua-as individualmente antes de excluir o talhão.',
                2291: 'Talhão de referência inexistente.',
                2290: 'Dados violam uma restrição de integridade.',
                942: 'Tabelas ausentes. Execute python main.py --init-db.'}.get(
                    code, 'Falha na operação Oracle. Confira o serviço, o .env e a conexão. Nenhuma alteração parcial foi confirmada.')
    return str(exc)
