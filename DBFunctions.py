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


    def lastEntry(self):

        conn = None

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

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return agora
    
    
    def lastEntryCep(self, cep):

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                SELECT *
                FROM leituras l
                where l.cep = {}
                ORDER BY "datahora" DESC LIMIT 1
                """.format(cep)
            )

            agora = cur.fetchall()

            #tratar exceção caso "dê ruim" no retorno do banco

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return agora
    
    
    def last15EntriesAvg(self):

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                SELECT AVG(fase1), AVG(fase2), AVG(fase3)
                FROM leituras
                """
            )

            agora = cur.fetchall()

            #tratar exceção caso "dê ruim" no retorno do banco

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
                from locais l 
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


    def interessadosCep(self, cep):
        """
            Retorna os chatIDs dos interessados no CEP fornecido
        """

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                select chatid 
                from alertados a 
                where a.cep = {};
                """.format(cep)
            )
            
            retorno = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return retorno


    def variouTensao(self, leitura):

        ultima = self.lastEntryCep(leitura['cep'])
        alerta = []
        
        if leitura['fase1'] != None: # if não tá funcionando
            if (leitura['fase1'] <= (0.05 * float(ultima[0][3]))) or (leitura['fase1'] > (0.05 * float(ultima[0][3]))):
                alerta.append(('Fase 1', leitura['fase1'], ultima[0][3]))
        
        if leitura['fase2'] != None:
            if (leitura['fase2'] <= (0.05 * float(ultima[0][4]))) or (leitura['fase2'] > (0.05 * float(ultima[0][4]))):
                alerta.append(('Fase 2', leitura['fase2'], ultima[0][4]))
        
        if leitura['fase3'] != None:
            if (leitura['fase3'] <= (0.05 * float(ultima[0][5]))) or (leitura['fase2'] > (0.05 * float(ultima[0][5]))):
                alerta.append(('Fase 3', leitura['fase3'], ultima[0][5]))
                
        if len(alerta) != 0:
            interessados = self.interessadosCep(leitura['cep'])
            for id in interessados:
                texto = 'Alertar Chat ID: {}\n'.format(id[0])
                texto += 'Variações observadas:\n'
                for a in alerta:
                    texto += '{}: de {}V para {}V\n'.format(
                        a[0],
                        str(a[1]).replace('.', ','),
                        str(a[2]).replace('.', ',')
                    )
                
                print(texto)

            # IMPLEMENTAR AONDE?
            # self.alertar(interessados, leitura)


    # def alertar(self, leitura):
