import sqlite3
from prettytable import PrettyTable


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.database = sqlite3.connect(db_name)
        self.cursor = self.database.cursor()
        self.table_names = []
        self.table = None

    def refer_tables(self):
        sql_query = "SELECT * FROM sqlite_master WHERE type='table' ORDER BY name;"
        self.cursor.execute(sql_query)
        return [t[1] for t in self.cursor.fetchall()]

    def create_table(self, table_name):
        try:
            create_query = f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY)'
            self.cursor.execute(create_query)
            self.database.commit()
        except Exception as e:
            print('Error(creating table)->', e)

    def delete_database(self):
        try:
            for table_name in self.refer_tables():
                drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
                print(f'Sql: "{drop_table_sql}"')
                self.cursor.execute(drop_table_sql)

            self.database.commit()
            print("...All of tables have been removed..")
        except Exception as e:
            print('!Error ->', e)

    def select(self, command):
        try:
            self.cursor.execute(command)
            table = PrettyTable()
            table.field_names = [h[0] for h in self.cursor.description]
            for row in self.cursor.fetchall():
                table.add_row(row)
            print(table)
        except Exception as e:
            print('!Error ->', e)

    def add_col(self, table_name:str, col_name: str, col_type: str):
        sql_query = f'ALTER TABLE {table_name} ADD {col_name} {col_type.upper()}'

        try:
            self.cursor.execute(sql_query)
            print('"Successfully Col has been added.."')
        except Exception as e:
            print(f'Sql: "{sql_query}"')
            print("!Error->", e)


class Shell:
    def __init__(self, db):
        self.db: Database = db
        self.prompt: str = f'$[~{self.db.db_name}]>>> '

    def fetch(self, command):
        try:
            if command.lower() == 'del':
                self.db.delete_database()
            elif command.split()[0].lower() == 'select':
                self.db.select(command)
            elif command.split()[0].lower() == 'col' and len(command.split()) == 3:
                _, col_name, col_type = command.split()
                if self.db.table:
                    self.db.add_col(self.db.table, col_name, col_type)
            elif command == 'ls':
                table_names = self.db.refer_tables()
                if len(table_names) > 0:
                    for i, table in enumerate(table_names):
                        print(f'{i + 1}. {table}')
                    print('...')
            elif command.split()[0].lower() == 'table' and len(command.split()) == 2:
                _, table_name = command.split()
                self.db.create_table(table_name)
            elif command.split()[0] == 'cd' and len(command.split()) == 2:
                _, target = command.split()
                if target == '../':
                    self.db.table = None
                    self.prompt = f'$[~PocketGuy]>>> '
                    return

                tables = self.db.refer_tables()
                if target in tables:
                    self.db.table = target
                    self.prompt = f'$[~PocketGuy/{self.db.table}]>>> '
                    return

                if target.isdigit() and 0 < len(target) <= len(tables):
                    self.db.table = tables[int(target) - 1]
                    self.prompt = f'$[~PocketGuy/{self.db.table}]>>> '
                    return

                print(f'!Error: incorrect Target({target})')
            else:
                self.db.cursor.execute(command)
                self.db.database.commit()
        except Exception as e:
            print(f'SQL: "{command}"')
            print('!Error(Executing Sql) ->', e)
