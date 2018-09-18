import sys
import sqlite3


class DBInterfacer():
    def __init__(self):
        self.db = sqlite3.connect('mydb')
        self.cursor = self.db.cursor()

    def __delattr__(self):
        print "DB IS GETTING CLOSED "
        self.db.close()

    def create_table(self, tablename, columns_dict):
        column_list = ["{0} {1}".format(col_name, col_type) for col_name, col_type in zip(columns_dict.keys(), columns_dict.values())]
        column_str = ', '.join(column_list)

        self.cursor.execute(
            '''CREATE TABLE if not exists {0}({1})'''.format(tablename, column_str))
        self.db.commit()

    def insert(self, tablename, info_dict):
        columns = ', '.join(info_dict.keys())
        placeholders = ', '.join('?' * len(info_dict))

        sql_str = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(tablename, columns, placeholders)
        print sql_str
        self.cursor.execute(sql_str, tuple(info_dict.values()))

        self.db.commit()

    def retrieve(self, tablename, columns=[], num_rows=0):
        if len(columns) == 0:
            column_str = "*"
        else:
            column_str = ', '.join(columns)

        self.cursor.execute(
            '''SELECT {0} FROM {1}'''.format(column_str, tablename))

        if num_rows > 0:
            return self.cursor.fetchall()[-num_rows:]

        return self.cursor.fetchall()

    def print_all_data(self, tablename):
        self.cursor.execute('''SELECT * FROM {0}'''.format(tablename))

        all_rows = self.cursor.fetchall()
        for row in all_rows:
            print row

    def describe_table(self, tablename):
        self.cursor.execute('''SELECT * FROM sqlite_master''')
        print self.cursor.fetchall()


def main():
    db = DBInterfacer()

    db.print_all_data("GameEvents")
   # db.describe_table("GameAudit")

    #print db.retrieve("GameAudit", ["game"], 1)

if __name__ == '__main__':
    main()

