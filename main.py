from sqlController import*


if __name__ == '__main__':
    db_name = 'Output'

    db = Database(db_name)
    for table_name in db.refer_tables():
        sql_query = f'select * from {table_name}'
        db.cursor.execute(sql_query)

        show_table = PrettyTable()
        show_table.field_names = [h[0] for h in db.cursor.description]
        for row in db.cursor.fetchall():
            show_table.add_row(row)

        print(f'<< {table_name} >>')
        print(show_table)
        print()
