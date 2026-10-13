import json
from unittest.mock import Mock
import pytest
from src.domain import Talhao
from src.files import read_json, export_json, validate_payload, atomic_write
from src.reports import report, export_txt
from src.cli import run, numeric, ask, Cancelled, read_date
from test_domain import sample


def test_json_roundtrip(tmp_path):
    path = tmp_path / 'dados.json'
    ts, cs = [Talhao('T01', 'São João', '10')], [sample()]
    export_json(path, ts, cs)
    assert read_json(path) == (ts, cs)
    assert 'São João' in path.read_text(encoding='utf-8')


@pytest.mark.parametrize('value', ['1e0', '1e-4', '1.00e1'])
def test_json_rejects_exponential_tokens(tmp_path, value):
    path = tmp_path / 'exponential.json'
    path.write_text('{"versao":1,"talhoes":[{"id":"T01","nome":"Teste",'
                    '"area_ha":' + value + '}],"colheitas":[]}', encoding='utf-8')
    with pytest.raises(ValueError, match='exponencial'):
        read_json(path)


def test_json_export_size_uses_bytes_and_preserves_original(tmp_path, monkeypatch):
    path = tmp_path / 'dados.json'
    ts, cs = [Talhao('T01', 'São João', '10')], [sample()]
    export_json(path, ts, cs)
    text = path.read_text(encoding='utf-8')
    size = len(text.encode('utf-8'))
    assert size > len(text)
    # O limite é em bytes UTF-8, incluindo acentos, e não em caracteres.
    monkeypatch.setattr('src.files.MAX_BYTES', size - 1)
    path.write_text('arquivo anterior', encoding='utf-8')
    with pytest.raises(ValueError, match='5 MiB'):
        export_json(path, ts, cs)
    assert path.read_text(encoding='utf-8') == 'arquivo anterior'
    assert list(tmp_path.iterdir()) == [path]
    monkeypatch.setattr('src.files.MAX_BYTES', size)
    export_json(path, ts, cs)
    assert read_json(path) == (ts, cs)


@pytest.mark.parametrize('text', ['{', '[]', '{}', '{"versao":1,"versao":1}',
    '{"versao":NaN}', '{"versao":Infinity}',
    '{"versao":true,"talhoes":[],"colheitas":[]}',
    '{"versao":1,"talhoes":{},"colheitas":[]}'])
def test_bad_json(tmp_path, text):
    path = tmp_path / 'bad.json'
    path.write_text(text)
    with pytest.raises(ValueError):
        read_json(path)


def test_missing_and_encoding(tmp_path):
    with pytest.raises(ValueError):
        read_json(tmp_path / 'missing')
    path = tmp_path / 'bad.json'
    path.write_bytes(b'\xff')
    with pytest.raises(ValueError):
        read_json(path)


def test_large_file(tmp_path):
    path = tmp_path / 'big.json'
    path.write_bytes(b' ' * (5 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match='5 MiB'):
        read_json(path)


@pytest.mark.parametrize('mode', ['duplicate', 'orphan', 'extra', 'missing', 'badrow'])
def test_integrity_payload(tmp_path, mode):
    path = tmp_path / 'data.json'
    export_json(path, [Talhao('T01', 'A', 10)], [sample()])
    data = json.loads(path.read_text())
    if mode == 'duplicate':
        data['talhoes'] *= 2
    elif mode == 'orphan':
        data['colheitas'][0]['talhao_id'] = 'T99'
    elif mode == 'extra':
        data['talhoes'][0]['extra'] = 1
    elif mode == 'missing':
        del data['colheitas'][0]['preco_t']
    else:
        data['talhoes'] = [False]
    with pytest.raises(ValueError):
        validate_payload(data)


def test_txt(tmp_path):
    path = tmp_path / 'report.txt'
    export_txt(path, [sample()])
    text = path.read_text(encoding='utf-8')
    assert 'R$ 3.000,00' in text
    assert 'Perdas: 20,0000 t' in text
    assert '2,50 %' in text
    assert 'Nenhuma colheita' in report([])


def test_atomic_write_failure_preserves_original(tmp_path, monkeypatch):
    path = tmp_path / 'data.txt'
    path.write_text('original')
    def fail(*args):
        raise OSError('Sem permissão')
    monkeypatch.setattr('src.files.os.replace', fail)
    with pytest.raises(OSError):
        atomic_write(path, 'new')
    assert path.read_text() == 'original'
    assert list(tmp_path.iterdir()) == [path]


def feed(monkeypatch, values):
    answers = iter(values)
    monkeypatch.setattr('builtins.input', lambda _: next(answers))


def test_numeric_retry_and_zero(monkeypatch, capsys):
    feed(monkeypatch, ['abc', '-1', '0'])
    assert numeric('Produção') == 0
    assert 'Atenção' in capsys.readouterr().out


def test_cancel(monkeypatch):
    feed(monkeypatch, ['0'])
    with pytest.raises(Cancelled):
        ask('ID')
    feed(monkeypatch, ['V'])
    with pytest.raises(Cancelled):
        numeric('Número')


def test_menus_and_exit(monkeypatch, capsys):
    repo = Mock()
    repo.talhoes.return_value = []
    feed(monkeypatch, ['x', '1', '2', '0', '0'])
    run(repo)
    out = capsys.readouterr().out
    assert 'Opção inválida' in out
    assert 'Nenhum talhão cadastrado' in out
    assert 'encerrado com segurança' in out
    repo.connection.rollback.assert_called_once()


def test_menu_handles_business_error(monkeypatch, capsys):
    repo = Mock()
    repo.talhoes.side_effect = ValueError('Teste de falha amigável')
    feed(monkeypatch, ['1', '2', '0', '0'])
    run(repo)
    assert 'Teste de falha amigável' in capsys.readouterr().out


def test_eof_exit(monkeypatch, capsys):
    def eof(_):
        raise EOFError()
    monkeypatch.setattr('builtins.input', eof)
    run(Mock())
    assert 'encerrado com segurança' in capsys.readouterr().out


@pytest.mark.parametrize('value', ['30/02/2026', '1/1/2026', '2026-01-01'])
def test_cli_dates(value):
    with pytest.raises(ValueError):
        read_date(value)
