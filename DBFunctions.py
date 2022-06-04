import psycopg2
from config import config
from datetime import datetime, date
from pycep_correios import get_address_from_cep, WebService, exceptions


class DBFunctions():


    def createDB(self):

        print('\nCriando tabelas do banco de dados...')

        conn = None

        try:
            # parâmetros de configuração do BD
            params = config()
            # conector do PostgreSQL BD
            conn = psycopg2.connect(**params)
            # cursor
            cur = conn.cursor()

            sql = """
                CREATE TABLE public.locais (
                    id serial NOT NULL,
                    datahora timestamp(0) NULL,
                    cep numeric(8) NULL,
                    nome bpchar(150) NULL,
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

                CREATE INDEX leituras_cep_idx ON public.leituras USING btree (cep);
            """

            # executa o SQL
            cur.execute(sql)
            # commita as mudanças
            conn.commit()
            # encerra a conexão com o BD
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('BD: Tabelas criadas!\n')


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


    def insertLocal(self, cep):

        agora = datetime.now()
        try:
            endereco = get_address_from_cep(str(cep), webservice=WebService.APICEP)
            local = '{}, {} - {}'.format(
                endereco['bairro'],
                endereco['cidade'],
                endereco['uf']
            )
        except (exceptions.CEPNotFound, exceptions.InvalidCEP):
            local = None

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO public.locais (datahora, cep, nome)
                VALUES(%s,%s,%s)
                """,
                (agora, cep, local)
            )

            conn.commit()
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('Local armazenado: "{}"!'.format(cep))
    
    
    def insertInteressado(self, chatId, cep):

        agora = datetime.now()
        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO alertados (datahora, chatid, cep)
                VALUES(%s,%s,%s)
                """,
                (agora, chatId, cep)
            )

            conn.commit()
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('{} monitorando {}-{}'.format(chatId, cep[:5], cep[5:]))
    
    
    def deleteInteressado(self, chatId, cep):

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM alertados a
                WHERE a.chatid = {} and a.cep = {}
                """.format(chatId, cep)
            )

            conn.commit()
            cur.close()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        print('{} abandonou {}-{}'.format(chatId, cep[:5], cep[5:]))


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
    
    
    def interessadoNoCep(self, chatId, cep):
        """
            Verifica se o chatId já está monitorando o CEP
        """

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                select * 
                from alertados a 
                where a.cep = {} and a.chatid = {}
                """.format(cep, chatId)
            )
            
            retorno = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return retorno
    
    
    def cepMonitorado(self, cep):
        """
            Verifica se o CEP fornecido possui monitoramento
        """

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                select * 
                from locais l 
                where l.cep = {};
                """.format(cep)
            )
            
            retorno = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return retorno
    
    
    def listarCepsMonitorados(self):
        """
            Retorna lista de CEPs em monitoramento
        """

        conn = None

        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute("""
                select cep, nome 
                from locais
                """
            )
            
            retorno = cur.fetchall()
        
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return retorno


    def variouTensao(self, leitura):

        anterior = self.lastEntryCep(leitura['cep'])
        texto = ''
        if anterior:
            if anterior[0][3] != None: a1 = float(anterior[0][3])
            if anterior[0][4] != None: a2 = float(anterior[0][4])
            if anterior[0][5] != None: a3 = float(anterior[0][5])
            f1 = leitura['fase1']
            f2 = leitura['fase2']
            f3 = leitura['fase3']
            porcentVaria = 0.05
            alerta = []
            
            if f1 != None:
                if (abs(f1 - a1) > (a1 * porcentVaria)):
                    alerta.append(('Fase 1', a1, f1))
                    print('Variou Fase 1!')
            
            if f2 != None:
                if (abs(f2 - a2) > (a2 * porcentVaria)):
                    alerta.append(('Fase 2', a2, f2))
                    print('Variou Fase 2!')
            
            if f3 != None:
                if (abs(f3 - a3) > (a3 * porcentVaria)):
                    alerta.append(('Fase 3', a3, f3))
                    print('Variou Fase 3!')
                    
            if alerta:
                texto += 'Variações observadas no CEP {}-{}:\n'.format(
                    str(leitura['cep'])[:5],
                    str(leitura['cep'])[5:]
                )
                for a in alerta:
                    texto += '{}: de {}V para {}V\n'.format(
                        a[0],
                        str(a[1]).replace('.', ','),
                        str(a[2]).replace('.', ',')
                    )

        return texto

