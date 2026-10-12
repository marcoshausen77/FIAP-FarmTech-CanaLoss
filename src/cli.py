"""Interface de terminal com navegação recuperável e confirmações explícitas."""
from pathlib import Path
from datetime import datetime
import oracledb
from .domain import Talhao, brazilian_number, harvest_date, identifier, name, simulate, alerts
from .files import read_json, export_json
from .reports import report, export_txt, fmt
from .oracle import friendly_error


class Cancelled(Exception):
    pass


def ask(prompt, validator=str):
    while True:
        text = input(prompt + ' [0 = voltar]: ').strip()
        if text == '0':
            raise Cancelled()
        try:
            return validator(text)
        except ValueError as exc:
            print(f'Atenção: {exc}')


def numeric(prompt, **kwargs):
    # Zero é um dado válido, portanto cancelar usa a letra V neste campo.
    while True:
        text = input(prompt + ' [V = voltar; vírgula decimal]: ').strip()
        if text.upper() == 'V':
            raise Cancelled()
        try:
            return brazilian_number(text, **kwargs)
        except ValueError as exc:
            print(f'Atenção: {exc}')


def read_date(text):
    try:
        if len(text) != 10:
            raise ValueError()
        dt = datetime.strptime(text, '%d/%m/%Y').date()
        if dt.strftime('%d/%m/%Y') != text:
            raise ValueError()
        return harvest_date(dt)
    except ValueError as exc:
        raise ValueError('Use uma data válida DD/MM/AAAA entre 01/01/1900 e hoje.') from exc


def confirmed(message):
    return input(message + ' Digite SIM para confirmar: ').strip().upper() == 'SIM'


def output_path():
    path = Path(ask('Caminho do arquivo'))
    if path.exists() and not confirmed('O arquivo existe e será substituído.'):
        raise Cancelled()
    return path


def choose_talhao(repo):
    talhoes = repo.talhoes()
    if not talhoes:
        raise ValueError('Nenhum talhão cadastrado.')
    for t in talhoes:
        print(f'{t.id} | {t.nome} | {fmt(t.area_ha, 4)} ha')
    valid = {t.id for t in talhoes}
    def check(text):
        value = identifier(text.upper())
        if value not in valid:
            raise ValueError('Escolha um identificador listado.')
        return value
    return ask('Talhão', check)


def talhoes_menu(repo):
    def create():
        repo.add_talhao(Talhao(ask('Identificador', lambda s: identifier(s.upper())),
                              ask('Nome', name), numeric('Área (ha)', positive=True)))
        print('Talhão cadastrado.')
    def show():
        rows = repo.talhoes()
        for t in rows:
            print(f'{t.id:<30} {t.nome} | {fmt(t.area_ha, 4)} ha')
        if not rows:
            print('Nenhum talhão cadastrado.')
    def edit():
        key = choose_talhao(repo)
        model = Talhao(key, ask('Novo nome', name), numeric('Nova área (ha)', positive=True))
        if confirmed('Atualizar cadastro? A área das colheitas anteriores será preservada.'):
            repo.edit_talhao(model)
            print('Talhão atualizado.')
    def delete():
        key = choose_talhao(repo)
        if confirmed(f'Excluir talhão {key}? Somente permitido sem colheitas.'):
            repo.delete('talhao', key)
            print('Talhão excluído.')
    menu('TALHÕES', [('Cadastrar', create), ('Consultar', show), ('Editar', edit), ('Excluir', delete)])


def measurements():
    return (ask('Data (DD/MM/AAAA)', read_date), numeric('Produção efetivamente colhida (t)'),
            numeric('Perda estimada (kg/ha)'), numeric('Preço de referência (R$/t)', positive=True))


def harvests_menu(repo):
    def create():
        key = choose_talhao(repo)
        print('Registre uma operação consolidada por talhão e dia, referente à área integral do talhão.')
        record_id = ask('Identificador da colheita', lambda s: identifier(s.upper()))
        values = measurements()
        if confirmed('Salvar colheita?'):
            record = repo.add_colheita(record_id, key, *values)
            print(report([record]))
    def edit():
        print(report(repo.colheitas()))
        key = ask('Identificador da colheita', lambda s: identifier(s.upper()))
        values = measurements()
        if confirmed('Corrigir colheita? O talhão e a área histórica serão mantidos.'):
            repo.edit_colheita(key, *values)
            print('Colheita atualizada.')
    def delete():
        print(report(repo.colheitas()))
        key = ask('Identificador da colheita', lambda s: identifier(s.upper()))
        if confirmed(f'Excluir definitivamente a colheita {key}?'):
            repo.delete('colheita', key)
            print('Colheita excluída.')
    def compare():
        records = repo.colheitas()
        print(report(records))
        a = ask('Primeiro identificador', lambda s: identifier(s.upper()))
        b = ask('Segundo identificador', lambda s: identifier(s.upper()))
        chosen = [r for r in records if r.id in {a, b}]
        if a == b or len(chosen) != 2:
            raise ValueError('Escolha duas colheitas diferentes e existentes.')
        print('COMPARAÇÃO — considere diferenças de área, período e preço.')
        print(report(chosen))
    menu('COLHEITAS', [('Registrar', create), ('Histórico e consolidado', lambda: print(report(repo.colheitas()))),
                      ('Consultar por talhão', lambda: print(report(repo.colheitas(choose_talhao(repo))))),
                      ('Comparar dois registros', compare), ('Corrigir registro', edit), ('Excluir registro', delete)])


def insights(repo):
    records = repo.colheitas()
    print(report(records))
    if not records:
        return
    limit = numeric('Limite de alerta de perda (%) — escolha conforme a operação', maximum=100)
    found = alerts(records, limit)
    for key, value in found:
        print(f'ALERTA: {key} — perda {fmt(value)} %, limite {fmt(limit)} %.')
    if not found:
        print('Nenhuma operação atingiu o limite informado.')
    values = []
    for i in range(1, 4):
        values.append(numeric(f'Redução relativa das perdas no cenário {i} (%)', maximum=100))
    print('\nSIMULAÇÕES HIPOTÉTICAS — receitas brutas potenciais, sem dedução de custos.')
    for row in simulate(records, values):
        print(f'{row["talhao_id"]} | redução {fmt(row["reducao_pct"])} % | '
              f'{fmt(row["recuperado_t"], 4)} t | R$ {fmt(row["recuperado_rs"])}')
    print('Priorize a verificação das áreas com maior prejuízo; confirme a amostragem das perdas,')
    print('as condições do terreno e a regulagem com o responsável técnico. Compare o custo da')
    print('intervenção com o potencial bruto. Estes cálculos não identificam causas nem garantem economia.')


def files_menu(repo):
    def load():
        path = ask('Caminho JSON para importar')
        ts, cs = read_json(path)
        if confirmed(f'Importar {len(ts)} talhões e {len(cs)} colheitas? Conflitos cancelarão todo o lote.'):
            repo.import_data(ts, cs)
            print('Importação concluída integralmente.')
    def save():
        path = output_path()
        export_json(path, *repo.snapshot())
        print('JSON exportado.')
    def txt():
        path = output_path()
        export_txt(path, repo.colheitas())
        print('Relatório TXT gerado.')
    menu('ARQUIVOS', [('Importar JSON', load), ('Exportar JSON', save), ('Gerar TXT', txt)])


def menu(title, options):
    while True:
        print(f'\n=== {title} ===')
        for i, (label, _) in enumerate(options, 1):
            print(f'{i}. {label}')
        print('0. Voltar / sair')
        choice = input('Opção: ').strip()
        if choice == '0':
            return
        if choice not in {str(i) for i in range(1, len(options) + 1)}:
            print('Opção inválida. Escolha um número do menu.')
            continue
        try:
            options[int(choice) - 1][1]()
        except Cancelled:
            print('Operação cancelada.')
        except (ValueError, OSError, oracledb.Error) as exc:
            print('Atenção: ' + friendly_error(exc))


def run(repo):
    print('CANALOSS | FIAP — Grupo 83 | Dados de colheita em Oracle')
    print('Entradas decimais: 1.250,50. Estimativas não equivalem a prejuízo auditado.')
    try:
        menu('PRINCIPAL', [('Talhões', lambda: talhoes_menu(repo)), ('Colheitas', lambda: harvests_menu(repo)),
                          ('CanaLoss Insights', lambda: insights(repo)), ('Importação e relatórios', lambda: files_menu(repo))])
    except (EOFError, KeyboardInterrupt):
        print('\nEntrada encerrada pelo usuário.')
    finally:
        repo.connection.rollback()
    print('CanaLoss encerrado com segurança.')
