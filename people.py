#usr/bin/python3
import argparse
from sys import stderr
from sqlite3 import connect
from contextlib import closing

DATABASE_URL = 'file:lux.sqlite?mode=ro' #TODO: need to update 

def parse():
    parser = argparse.ArgumentParser(description='', allow_abbrev=False)
    parser.add_argument('-u', metavar='username', type=str, help='person\'s username')
    parser.add_argument('-d', metavar='joined date', type=str, help='what date the person joined the site')
    parser.add_argument('-l', metavar='lost', type=str, help='number of lost items')
    parser.add_argument('-f', metavar='found', type=str, help='number of found items')
    parser.add_argument('-s', metavar='admin status', type=str, help='whether admin or not')

    parser.add_argument('-o', type=str, choices=['add', 'update', 'delete', 'get'])

    args = parser.parse_args()

    return args

def main(args):
    try:
        with connect(DATABASE_URL, isolation_level=None, uri=True) as connection:

            with closing(connection.cursor()) as cursor:
                # Create a prepared statement and substitute values.
                argsStore = []
                if args.o == 'add':
                    stmt_str = 'INSERT INTO People (username, joined_date, lost, found, admin_status) VALUES (?,?,?,?,?);'
                    argsStore.append(args.u)
                    argsStore.append(args.d)
                    argsStore.append(args.l)
                    argsStore.append(args.f)
                    argsStore.append(args.s)

                elif args.o == 'update':
                    stmt_str = 'UPDATE People SET '
                    update_conds = []
                    if args.d:
                        update_conds.append('joined_date = ?')
                        argsStore.append(args.d)
                    if args.l:
                        update_conds.append('lost = ?')
                        argsStore.append(args.l)
                    if args.f:
                        update_conds.append('found = ?')
                        argsStore.append(args.f)
                    if args.s:
                        update_conds.append('found = ?')
                        argsStore.append(args.f)

                    stmt_str += update_conds.join(', ')
                    stmt_str += 'WHERE username = ?'
                    argsStore.append(args.u)

                elif args.o == 'get':
                    stmt_str = 'SELECT '
                    select_conds = []
                    if args.u:
                        select_conds.append('username')
                    if args.d:
                        select_conds.append('joined_date')
                    if args.l:
                        select_conds.append('lost')
                    if args.f:
                        select_conds.append('found')
                    if args.s:
                        select_conds.append('admin_status')
                    stmt_str += select_conds.join(', ')

                    stmt_str += ' FROM People WHERE username = ?'
                    argsStore.append(args.u)

                else: #args.o == 'delete':
                    stmt_str = 'DELETE * FROM People WHERE username = ?'
                    argsStore.append(args.u)

                cursor.execute(stmt_str, tuple(argsStore))
                row = cursor.fetchone()
                data = []
                while row is not None:
                    data.append(row)
                    row = cursor.fetchone()

                # Create Table
                print(f"Search Produced {len(data)} objects.")
                print(data)

    except Exception as ex:
        print(ex)
        exit(1)

if __name__ == '__main__':
    args = parse()
    main(args)
