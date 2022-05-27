import psycopg2
from config import config
from datetime import datetime, date, timezone


class DBFunctions():


    def createDB(self):

        print('\nCriando o banco de dados...')

        sql = """CREATE TABLE public.locais (
                        id serial NOT NULL,
                        datahora timestamp(0) NULL,
                        cep numeric(8) NULL,
                        nome bpchar(50) NULL,
                        CONSTRAINT locais_pkey PRIMARY KEY (id)
                    );

                    CREATE TABLE public.alertados (
                        id serial NOT NULL,
                        datahora timestamp(0) NULL,
                        chatid int4 NULL,
                        cep numeric(8) NULL,
                        CONSTRAINT alertados_pk PRIMARY KEY (id)
                    );

                    CREATE TABLE public.leituras (
                        id serial NOT NULL,
                        datahora timestamp(0) NULL,
                        cep numeric(8) NULL,
                        fase1 numeric(5,2) NULL,
                        fase2 numeric(5,2) NULL,
                        fase3 numeric(5,2) NULL,
                        temperatura numeric(4,2) NULL,
                        humidade numeric(3) NULL,
                        choveagora bool NULL,
                        CONSTRAINT leituras_pkey PRIMARY KEY (id)
                    );

                    CREATE INDEX locais_cep_idx ON public.locais USING btree (cep);

                    CREATE INDEX leituras_cep_idx ON public.leituras USING btree (cep);"""
        
        conn = self.createConnection(self.file)

        if conn is not None:
            self.createTable(conn, sql)
            conn.close()
        else:
            print("\nErro: não foi possível estabelecer conexão com o banco de dados.")


    def insertLeitura(self, leitura):

        # verificar se já existe cep cadastrado na tabela locais
        if self.existeLocalCadastrado(leitura['cep']) == False:
            self.insertLocal(leitura['cep'])

        agora = datetime.now()

        conn = None

        try:
            # parâmetros de configuração do BD
            params = config()
            # conector do PostgreSQL BD
            conn = psycopg2.connect(**params)
            # cursor
            cur = conn.cursor()
            # executa o SQL
            cur.execute("""
                INSERT INTO public.leituras (datahora, cep, fase1, fase2, fase3, temperatura, humidade, choveagora)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (agora, leitura['cep'], leitura['fase1'], leitura['fase2'], leitura['fase3'], leitura['temperatura'], leitura['humidade'], leitura['chove'])
            )

            # commita as mudanças
            conn.commit()
            # encerra a conexão com o BD
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('Leitura armazenada!\n')


    def insertLocal(self, local):

        agora = datetime.now()

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO public.locais (datahora, cep, nome)
                VALUES(%s,%s,%s)
                """,
                (agora, local, None)
            )

            conn.commit()
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('Local armazenado: "{}"!'.format(local))


    def todaysAvg(self):

        conn = None
        avg = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            
            cur.execute(
                """SELECT AVG(fase1), AVG(fase2), AVG(fase3), count(*)
                FROM leituras
                WHERE datahora::text LIKE '{}%'
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
                ORDER BY "datahora" DESC LIMIT 1
                """
            )

            agora = cur.fetchall()

            #tratar exceção caso "dê ruim" no retorno do banco
            # formatado = agora[0][1].strftime('%d/%m/%Y'), agora[0][1].strftime('%H:%M:%S'), agora[0][3]

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return agora


    def existeLocalCadastrado(self, cep):

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                select * 
                from public.locais l 
                where l.cep = {} limit 1;
                """.format(cep)
            )
            
            retorno = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return bool(retorno)

