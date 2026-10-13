"""Modelos e regras de negócio independentes da interface e do banco."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, getcontext
import re

# Margem para produtos e consolidações de valores extremos sem perder centavos.
getcontext().prec = 50

ZERO = Decimal('0')
MAX_VALUE = Decimal('1000000000')


def number(value, label='Valor', *, positive=False, maximum=MAX_VALUE):
    """Formato canônico do domínio/JSON: ponto decimal, sem milhares."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f'{label}: informe um número válido.')
    text = str(value).strip()
    if len(text) > 40 or not re.fullmatch(r'-?\d+(?:\.\d+)?', text):
        raise ValueError(f'{label}: número inválido; use até quatro casas decimais.')
    try:
        result = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f'{label}: número inválido.') from exc
    if not result.is_finite() or result < 0 or (positive and result == 0) or result > maximum:
        raise ValueError(f'{label}: deve ser {"maior que zero" if positive else "não negativo"} e até {maximum}.')
    if result.as_tuple().exponent < -4:
        raise ValueError(f'{label}: máximo de quatro casas decimais.')
    return result


def brazilian_number(text, **kwargs):
    """Terminal usa vírgula decimal e ponto apenas em milhares agrupados."""
    if not isinstance(text, str):
        raise ValueError('Digite um número, por exemplo 1.250,50.')
    text = text.strip()
    if not re.fullmatch(r'-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,4})?', text):
        raise ValueError('Use vírgula decimal: 12,5 ou 1.250,50; não use ponto decimal.')
    return number(text.replace('.', '').replace(',', '.'), **kwargs)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{0,29}', value):
        raise ValueError('Identificador: 1 a 30 letras maiúsculas, números, hífen ou sublinhado.')
    return value


def name(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 100 or any(ord(c) < 32 for c in value):
        raise ValueError('Nome: informe de 1 a 100 caracteres, sem quebras de linha.')
    return value.strip()


def harvest_date(value):
    if type(value) is date:
        result = value
    elif isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        try:
            result = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError('Data inválida. Use AAAA-MM-DD.') from exc
    else:
        raise ValueError('Data inválida. Use AAAA-MM-DD.')
    if result < date(1900, 1, 1) or result > date.today():
        raise ValueError('A data deve estar entre 1900-01-01 e hoje.')
    return result


@dataclass(frozen=True)
class Talhao:
    id: str
    nome: str
    area_ha: Decimal

    def __post_init__(self):
        identifier(self.id)
        object.__setattr__(self, 'nome', name(self.nome))
        object.__setattr__(self, 'area_ha', number(self.area_ha, 'Área', positive=True))


@dataclass(frozen=True)
class Colheita:
    id: str
    talhao_id: str
    data: date
    area_ha: Decimal
    producao_t: Decimal
    perda_kg_ha: Decimal
    preco_t: Decimal

    def __post_init__(self):
        identifier(self.id)
        identifier(self.talhao_id)
        object.__setattr__(self, 'data', harvest_date(self.data))
        for field, label, positive in [('area_ha', 'Área', True), ('producao_t', 'Produção', False),
                                        ('perda_kg_ha', 'Perda', False), ('preco_t', 'Preço', True)]:
            object.__setattr__(self, field, number(getattr(self, field), label, positive=positive))


def calculate(record):
    lost = record.area_ha * record.perda_kg_ha / Decimal(1000)
    total = record.producao_t + lost
    return {'perda_t': lost, 'total_t': total,
            'percentual': lost / total * 100 if total else None,
            'prejuizo': lost * record.preco_t}


def consolidated(records):
    """Tabela em memória (lista de dicionários), agrupada por talhão."""
    table = {}
    for record in records:
        row = table.setdefault(record.talhao_id, {'talhao_id': record.talhao_id,
                              'producao_t': ZERO, 'perda_t': ZERO, 'prejuizo': ZERO, 'registros': 0})
        result = calculate(record)
        row['producao_t'] += record.producao_t
        row['perda_t'] += result['perda_t']
        row['prejuizo'] += result['prejuizo']
        row['registros'] += 1
    return sorted(table.values(), key=lambda row: (-row['prejuizo'], row['talhao_id']))


def simulate(records, percentages):
    """Cenários hipotéticos: redução relativa da massa perdida, não pontos percentuais."""
    rows = consolidated(records)
    scenarios = []
    for value in percentages:
        percent = number(value, 'Redução (%)', maximum=Decimal(100))
        for row in rows:
            scenarios.append({'talhao_id': row['talhao_id'], 'reducao_pct': percent,
                              'recuperado_t': row['perda_t'] * percent / 100,
                              'recuperado_rs': row['prejuizo'] * percent / 100})
    return scenarios


def alerts(records, limit):
    threshold = number(limit, 'Limite (%)', maximum=Decimal(100))
    return [(r.id, calculate(r)['percentual']) for r in records
            if calculate(r)['percentual'] is not None and calculate(r)['percentual'] >= threshold]
