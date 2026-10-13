"""Integração real: nunca usar mocks, SQLite ou dados persistentes de produção."""
import os
from uuid import uuid4
from decimal import Decimal
import pytest
import oracledb
from src.oracle import connect, initialize, Repository
from src.domain import Talhao, Colheita
from src.files import export_json, read_json
from src.cli import run

pytestmark = [pytest.mark.integration,
              pytest.mark.skipif(os.getenv('RUN_ORACLE_TESTS') != '1',
                                 reason='Requer Oracle real e RUN_ORACLE_TESTS=1')]


@pytest.fixture
def repo():
    # IDs exclusivos; limpeza somente dos dados criados por este módulo.
    with connect() as conn:
        initialize(conn)
        r = Repository(conn)
        r.prefix = 'TEST_' + uuid4().hex[:10].upper()
        yield r
        conn.rollback()
        with conn.cursor() as c:
            c.execute('DELETE FROM colheitas WHERE SUBSTR(id, 1, :n) = :prefix', n=len(r.prefix), prefix=r.prefix)
            c.execute('DELETE FROM talhoes WHERE SUBSTR(id, 1, :n) = :prefix', n=len(r.prefix), prefix=r.prefix)
        conn.commit()


def create(repo):
    t = Talhao(repo.prefix + '_T', 'Integração fictícia', '10')
    repo.add_talhao(t)
    record = repo.add_colheita(repo.prefix + '_C', t.id, '2026-01-01', '780', '2000', '150')
    return t, record


def test_real_connection_crud_snapshot(repo):
    print('Oracle real:', repo.connection.version)
    assert repo.connection.version
    t, r = create(repo)
    # Uma segunda conexão comprova commit, não somente estado da sessão.
    with connect() as second:
        assert r in Repository(second).colheitas(t.id)
    repo.edit_talhao(Talhao(t.id, 'Área atualizada', 20))
    assert repo.colheitas(t.id)[0].area_ha == 10
    repo.edit_colheita(r.id, '2026-01-02', 800, 1000, 160)
    stored = repo.colheitas(t.id)[0]
    assert stored.producao_t == 800 and stored.preco_t == 160 and stored.area_ha == 10
    ts, cs = repo.snapshot()
    assert stored in cs and any(row.id == t.id and row.area_ha == 20 for row in ts)
    repo.delete('colheita', r.id)
    repo.delete('talhao', t.id)
    assert repo.colheitas(t.id) == []


def test_duplicate_fk_and_checks(repo):
    t, r = create(repo)
    with pytest.raises(oracledb.IntegrityError):
        repo.add_talhao(t)
    with pytest.raises(oracledb.IntegrityError):
        repo.delete('talhao', t.id)
    with pytest.raises(oracledb.IntegrityError):
        repo.add_colheita(repo.prefix + '_D', t.id, '2026-01-01', 1, 1, 1)
    with repo.connection.cursor() as c:
        for area in (0, -1, Decimal('0.00001')):
            with pytest.raises(oracledb.IntegrityError):
                c.execute('UPDATE talhoes SET area_ha=:area WHERE id=:id', area=area, id=t.id)
            repo.connection.rollback()
        with pytest.raises(oracledb.IntegrityError):
            c.execute('UPDATE colheitas SET talhao_id=:missing WHERE id=:id',
                      missing=repo.prefix + '_MISSING', id=r.id)
        repo.connection.rollback()
    assert repo.colheitas(t.id) == [r]


def test_import_rollback_after_partial_insert(repo):
    t, r = create(repo)
    new = Talhao(repo.prefix + '_NEW', 'Novo', 5)
    valid = Colheita(repo.prefix + '_V', new.id, '2026-02-01', 5, 30, 500, 100)
    before = repo.snapshot()
    with pytest.raises(oracledb.IntegrityError):
        repo.import_data([t, new], [valid, r])
    assert repo.snapshot() == before  # inclui exclusão dos INSERTs anteriores ao conflito


def test_import_export_and_conflicting_talhao(repo, tmp_path):
    t = Talhao(repo.prefix + '_T', 'Arquivo', 10)
    r = Colheita(repo.prefix + '_C', t.id, '2026-01-01', 10, 780, 2000, 150)
    path = tmp_path / 'data.json'
    export_json(path, [t], [r])
    repo.import_data(*read_json(path))
    assert repo.colheitas(t.id) == [r]
    with pytest.raises(ValueError, match='diferentes'):
        repo.import_data([Talhao(t.id, 'Conflito', 20)], [])
    assert t in repo.talhoes()


def test_missing_and_sql_injection(repo):
    with pytest.raises(ValueError):
        repo.add_colheita(repo.prefix + '_C', repo.prefix + '_M', '2026-01-01', 1, 1, 1)
    with pytest.raises(ValueError):
        repo.delete('talhao', "X' OR '1'='1")
    with pytest.raises(ValueError):
        repo.edit_talhao(Talhao(repo.prefix + '_M', 'Ausente', 1))
    with pytest.raises(ValueError):
        repo.edit_colheita(repo.prefix + '_M', '2026-01-01', 1, 1, 1)
    # Nome hostil é armazenado como texto literal via bind.
    t = Talhao(repo.prefix + '_T', "Cana'); DROP TABLE talhoes; --", 1)
    repo.add_talhao(t)
    assert t in repo.talhoes()


def test_cli_real_create_consult_exit(repo, monkeypatch, capsys):
    tid = repo.prefix + '_T'
    answers = iter(['1', '1', tid, 'Talhão da apresentação', '10', '2', '0', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    run(repo)
    assert any(t.id == tid for t in repo.talhoes())
    output = capsys.readouterr().out
    assert 'Talhão cadastrado.' in output and 'encerrado com segurança' in output


def test_snapshot_empty_talhao_and_decimal_precision(repo, tmp_path):
    t = Talhao(repo.prefix + '_T', 'Sem colheita', '0.0001')
    repo.add_talhao(t)
    ts, cs = repo.snapshot()
    assert t in ts and not any(r.talhao_id == t.id for r in cs)
    r = repo.add_colheita(repo.prefix + '_C', t.id, '2026-02-01', '0.0001', '0.0001', '0.0001')
    assert r in repo.snapshot()[1]
    path = tmp_path / 'snapshot.json'
    export_json(path, *repo.snapshot())
    assert r in read_json(path)[1]


def test_cli_full_flow_real_oracle(repo, monkeypatch, capsys, tmp_path):
    t, r = create(repo)
    json_path, txt_path = tmp_path / 'export.json', tmp_path / 'export.txt'
    answers = iter(['2', '3', t.id, '0', '3', '2', '5', '15', '30',
                    '4', '2', str(json_path), '3', str(txt_path),
                    '1', str(json_path), 'SIM', '0', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    run(repo)
    assert r in read_json(json_path)[1]
    assert 'R$ 3.000,00' in txt_path.read_text(encoding='utf-8')
    out = capsys.readouterr().out
    assert 'SIMULAÇÕES HIPOTÉTICAS' in out and 'R$ 450,00' in out
    assert 'Identificador duplicado' in out
    assert repo.colheitas(t.id) == [r]
