from datetime import date
from decimal import Decimal as D
import pytest
from src.domain import (Talhao, Colheita, number, brazilian_number, identifier,
                        harvest_date, calculate, consolidated, simulate, alerts)


def sample(**changes):
    args = dict(id='C01', talhao_id='T01', data='2026-01-01', area_ha='10',
                producao_t='780', perda_kg_ha='2000', preco_t='150')
    args.update(changes)
    return Colheita(**args)


def test_known_calculation():
    assert calculate(sample()) == {'perda_t': D(20), 'total_t': D(800),
                                  'percentual': D('2.5'), 'prejuizo': D(3000)}


def test_zero_total_is_undefined():
    assert calculate(sample(producao_t=0, perda_kg_ha=0))['percentual'] is None
    assert calculate(sample(producao_t=0))['percentual'] == 100
    assert alerts([sample(producao_t=0, perda_kg_ha=0)], 0) == []


def test_ranking_and_scenarios():
    records = [sample(), sample(id='C02', talhao_id='T02', perda_kg_ha=1000),
               sample(id='C03', data='2026-01-02')]
    rows = consolidated(records)
    assert [r['talhao_id'] for r in rows] == ['T01', 'T02']
    assert rows[0]['prejuizo'] == 6000
    scenarios = simulate(records, [0, 15, 100])
    assert scenarios[2]['recuperado_t'] == 6
    assert scenarios[2]['recuperado_rs'] == 900
    assert scenarios[0]['recuperado_rs'] == 0
    assert scenarios[4]['recuperado_rs'] == 6000
    assert alerts([sample()], '2.5') == [('C01', D('2.5'))]
    assert alerts([sample()], '2.5001') == []


@pytest.mark.parametrize('value', [None, True, False, [], {}, '', 'abc', '-1', 'NaN',
    'Infinity', float('inf'), float('nan'), '1e999', '1.00001', '1000000001', '1,5', '9' * 100])
def test_invalid_numeric(value):
    with pytest.raises(ValueError):
        number(value)


@pytest.mark.parametrize('value,expected', [('0', '0'), ('1.250,50', '1250.50'),
    ('12,5', '12.5'), ('1.000', '1000'), ('0,0001', '0.0001'), (' 10 ', '10')])
def test_brazilian(value, expected):
    assert brazilian_number(value) == D(expected)


@pytest.mark.parametrize('value', ['1.25', '1,000.50', '1.00,5', '1,,2', 'NaN', '', '-5', '1,00001'])
def test_bad_brazilian(value):
    with pytest.raises(ValueError):
        brazilian_number(value)


@pytest.mark.parametrize('value', ['2026-02-30', '2026-13-01', '2100-01-01', '1899-12-31',
    '20260101', '01/01/2026', None, True])
def test_invalid_dates(value):
    with pytest.raises(ValueError):
        harvest_date(value)


def test_leap_day():
    assert harvest_date('2024-02-29') == date(2024, 2, 29)
    with pytest.raises(ValueError):
        harvest_date('2025-02-29')


@pytest.mark.parametrize('value', ['', 'a', "T'; DROP TABLE talhoes;--", 'A' * 31, None, 'T 1'])
def test_invalid_identifiers(value):
    with pytest.raises(ValueError):
        identifier(value)


@pytest.mark.parametrize('args', [('T1', '', 1), ('T1', 'Bom', 0), ('T1', 'Bom', -1), ('T1', 'a\nb', 1)])
def test_invalid_talhao(args):
    with pytest.raises(ValueError):
        Talhao(*args)


@pytest.mark.parametrize('percent', [-1, 101, 'NaN', None])
def test_invalid_scenario(percent):
    with pytest.raises(ValueError):
        simulate([sample()], [percent])


def test_limits_and_precision():
    r = sample(area_ha='1000000000', perda_kg_ha='1000000000', preco_t='1000000000')
    assert calculate(r)['prejuizo'] == D('1000000000000000000000000')
    assert number('0.0001', positive=True) == D('0.0001')
    with pytest.raises(ValueError):
        sample(preco_t=0)


def test_report_many_extreme_records():
    from src.reports import report
    rows = [sample(id=f'C{i}', area_ha='1000000000', perda_kg_ha='1000000000',
                   preco_t='1000000000') for i in range(1000)]
    assert '1.000.000.000.000.000.000.000.000.000,00' in report(rows)
