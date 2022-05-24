import sqlite3, json, re, psycopg2
from config import config
from datetime import datetime, date, timezone


class DBFunctions():

    # conn = psycopg2.connect("dbname=projetoTCC user=postgres password=Ci$coto$")

    # conn = psycopg2.connect(
    #     host="localhost",
    #     database="projetoTCC",
    #     user="postgres",
    #     password="Ci$coto$"
    # )

    # file = 'leiturasEsp32.db'
    ultimaLeitura = []

    # def createConnection(self, dbFile):
        
    #     conn = None
        
    #     try:
    #         conn = sqlite3.connect(dbFile)
    #         return conn
    #     except sqlite3.Error as e:
    #         print(e)
        
    #     return conn


    # def createDB(self):
    #     print('\nCriando o banco de dados...')

    #     sql = """CREATE TABLE IF NOT EXISTS leituras (
    #             data DATE,
    #             place CHAR(20),
    #             tensao NUMERIC(3,1),
    #             temperatura NUMERIC(2,1),
    #             humidade NUMERIC(3),
    #             choveAgora BOOLEAN
    #         )"""
        
    #     conn = self.createConnection(self.file)

    #     if conn is not None:
    #         self.createTable(conn, sql)
    #         conn.close()
    #     else:
    #         print("\nErro: não foi possível estabelecer conexão com o banco de dados.")


    def insertLeitura(self, place, tensao, temperatura, umidade, chove):

        agora = datetime.now()

        conn = None

        try:
            # read database configuration
            params = config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            # create a new cursor
            cur = conn.cursor()
            # execute the INSERT statement
            cur.execute("""
                INSERT INTO leituras (dataleitura, place, tensao, temperatura, humidade, choveagora)
                VALUES(%s,%s,%s,%s,%s,%s)
                """,
                (agora, place, tensao, temperatura, umidade, chove,)
            )

            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('Leitura armazenada!\n')

    
    def todaysAvg(self):

        conn = None
        avg = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            
            cur.execute(
                """SELECT AVG(tensao), count(*)
                FROM leituras
                WHERE dataleitura::text LIKE '{}%'
                """.format(date.today())
            )
            conn.commit()
            avg = cur.fetchall()
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return avg
    
    
    def now(self):

        conn = None
        formatado = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                SELECT *
                FROM leituras
                ORDER BY "dataleitura" DESC LIMIT 1
                """
            )
            
            agora = cur.fetchall()
            #tratar exceção caso "dê ruim" no retorno do banco
            formatado = agora[0][0].strftime('%d/%m/%Y'), agora[0][0].strftime('%H:%M:%S'), agora[0][2]
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return formatado

