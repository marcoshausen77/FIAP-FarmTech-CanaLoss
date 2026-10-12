"""Ponto de entrada: python main.py; inicializar esquema: --init-db."""
import argparse
import sys
import oracledb
from src.oracle import connect, initialize, Repository, friendly_error
from src.cli import run


def main():
    parser = argparse.ArgumentParser(description='CanaLoss — FIAP, Grupo 83')
    parser.add_argument('--init-db', action='store_true', help='Criar tabelas ausentes no Oracle')
    args = parser.parse_args()
    try:
        with connect() as connection:
            if args.init_db:
                initialize(connection)
                print('Esquema Oracle disponível.')
            else:
                run(Repository(connection))
        return 0
    except (ValueError, oracledb.Error) as exc:
        print('Atenção: ' + friendly_error(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('\nInicialização cancelada.')
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
