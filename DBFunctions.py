import sqlite3, json, re
from datetime import datetime, date


class DBFunctions():

    file = 'leiturasEsp32.db'

    def createConnection(self, dbFile):
        
        conn = None
        
        try:
            conn = sqlite3.connect(dbFile)
            return conn
        except sqlite3.Error as e:
            print(e)
        
        return conn
    

    def createTable(self, conn, createTableSql):
        
        try:
            cursor = conn.cursor()
            cursor.execute(createTableSql)
        except sqlite3.Error as e:
            print(e)
        
        print('\nBanco de dados criado!\n')
        

    def createDB(self):
        print('\nCriando o banco de dados...')

        sql = """CREATE TABLE IF NOT EXISTS leituras (
                data DATE,
                local CHAR(20),
                tensao NUMERIC(3,1),
                temperatura NUMERIC(2,1),
                humidade NUMERIC(3),
                choveAgora BOOLEAN
            )"""
        
        conn = self.createConnection(self.file)

        if conn is not None:
            self.createTable(conn, sql)
            conn.close()
        else:
            print("\nErro: não foi possível estabelecer conexão com o banco de dados.")


    def insertLeitura(self, local, tensao, temperatura, umidade, chove):

        conn = self.createConnection(self.file)

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leituras (data, local, tensao, temperatura, humidade, choveAgora)
                VALUES (?,?,?,?,?,?)
                """,
                (datetime.now(), local, tensao, temperatura, umidade, chove)
            )
        except sqlite3.Error as e:
            print(e)

        conn.commit()
        conn.close()

        print('Leitura armazenada!\n')

    
    def todaysAvg(self):

        conn = self.createConnection(self.file)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """SELECT avg(tensao), count(*)
                FROM leituras
                WHERE leituras.data like "{}%"
                """.format(date.today())
            )
        except sqlite3.Error as e:
            print(e)

        avg = cursor.fetchall()
        conn.close()

        return avg
    
    
    # def executeSelect(self, sql):
        
    #     conn = self.createConnection(self.file)

    #     try:
    #         cursor = conn.cursor()
    #         cursor.execute(sql)
    #     except sqlite3.Error as e:
    #         print(e)

    #     conn.commit()
    #     conn.close()
