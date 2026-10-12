"""Apresentação em português; arredondamento apenas na exibição."""
from decimal import Decimal, ROUND_HALF_UP
from .domain import calculate, consolidated
from .files import atomic_write


def fmt(value, places=2):
    if value is None:
        return 'N/D'
    rounded = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    return f'{rounded:,.{places}f}'.translate(str.maketrans(',.', '.,'))


def report(records):
    lines = ['CANALOSS | RELATÓRIO DE PERDAS ESTIMADAS', '=' * 100,
             'Dados registrados; valores estimados, sem garantia de recuperação.',
             'A área histórica de cada operação é preservada.', '',
             f'{"Registro":<30} {"Talhão":<30} {"Data":<10}',
             '  Área (ha) | Colhida (t) | Perdida (t) | Total estimado (t) | Perda (%) | Prejuízo (R$)']
    for r in records:
        v = calculate(r)
        lines += [f'{r.id:<30} {r.talhao_id:<30} {r.data:%d/%m/%Y}',
                  '  ' + ' | '.join([fmt(r.area_ha, 4), fmt(r.producao_t, 4), fmt(v['perda_t'], 4),
                                     fmt(v['total_t'], 4), fmt(v['percentual']), fmt(v['prejuizo'])])]
    rows = consolidated(records)
    collected = sum((r.producao_t for r in records), Decimal(0))
    lost = sum((r['perda_t'] for r in rows), Decimal(0))
    money = sum((r['prejuizo'] for r in rows), Decimal(0))
    total = collected + lost
    lines += ['', f'Registros: {len(records)}', f'Produção colhida: {fmt(collected, 4)} t',
              f'Perdas: {fmt(lost, 4)} t', f'Produção total estimada: {fmt(total, 4)} t',
              f'Percentual consolidado ponderado: {fmt(lost / total * 100 if total else None)} %',
              f'Prejuízo estimado: R$ {fmt(money)}', '', 'RANKING POR IMPACTO FINANCEIRO']
    lines.extend(f'{i}. {r["talhao_id"]}: R$ {fmt(r["prejuizo"])} | {fmt(r["perda_t"], 4)} t | {r["registros"]} operação(ões)'
                 for i, r in enumerate(rows, 1))
    if not records:
        lines.append('Nenhuma colheita registrada.')
    lines += ['', 'N/D: percentual indefinido quando produção colhida e perda são zero.',
              'O ranking soma operações e períodos; não mede isoladamente a eficiência por hectare.']
    return '\n'.join(lines) + '\n'


def export_txt(path, records):
    atomic_write(path, report(records))
