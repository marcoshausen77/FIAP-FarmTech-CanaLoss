"""JSON versionado, validação integral e escrita atômica de arquivos."""
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from pathlib import Path
import json
import os
import tempfile
from .domain import Talhao, Colheita

MAX_BYTES = 5 * 1024 * 1024


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Chave JSON repetida: {key}.')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f'Constante JSON inválida: {value}.')


def validate_payload(payload):
    if not isinstance(payload, dict) or set(payload) != {'versao', 'talhoes', 'colheitas'}:
        raise ValueError('JSON deve conter somente versao, talhoes e colheitas.')
    if type(payload['versao']) is not int or payload['versao'] != 1:
        raise ValueError('Versão JSON não suportada; use 1.')
    for key in ('talhoes', 'colheitas'):
        if not isinstance(payload[key], list) or len(payload[key]) > 10000:
            raise ValueError(f'{key}: informe uma lista com até 10.000 registros.')
    try:
        talhoes = [Talhao(**row) for row in payload['talhoes']]
        colheitas = [Colheita(**row) for row in payload['colheitas']]
    except (TypeError, KeyError) as exc:
        raise ValueError('Campos ausentes, extras ou estrutura de registro inválida.') from exc
    ids = {t.id for t in talhoes}
    if len(ids) != len(talhoes) or len({c.id for c in colheitas}) != len(colheitas):
        raise ValueError('Identificadores duplicados no arquivo.')
    if any(c.talhao_id not in ids for c in colheitas):
        raise ValueError('Toda colheita deve referenciar um talhão incluído no arquivo.')
    return talhoes, colheitas


def read_json(path):
    try:
        with Path(path).open('rb') as handle:
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Arquivo excede o limite de 5 MiB.')
        payload = json.loads(data.decode('utf-8-sig'), parse_float=Decimal,
                             parse_constant=invalid_constant, object_pairs_hook=unique_pairs)
        return validate_payload(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('Não foi possível ler o JSON: arquivo ausente, inacessível ou corrompido.') from exc


def atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         delete=False, newline='\n') as handle:
            temporary = handle.name
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def json_default(value):
    if isinstance(value, Decimal):
        return format(value, 'f')
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError('Tipo não serializável.')


def export_json(path, talhoes, colheitas):
    payload = {'versao': 1, 'talhoes': [asdict(t) for t in talhoes],
               'colheitas': [asdict(c) for c in colheitas]}
    validate_payload(payload)
    atomic_write(path, json.dumps(payload, default=json_default, ensure_ascii=False, indent=2) + '\n')
