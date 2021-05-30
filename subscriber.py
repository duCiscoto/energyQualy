import sqlite3, json, re
from datetime import datetime
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "tccEngSoftwareECC/Metropolitan"

client_id = 'assinanteTcc'
username = ''
password = ''

# # conecta ao banco de dados
# conn = sqlite3.connect('leiturasEsp32.db')

# # define um cursor (navega e manipula registros no banco)
# cursor = conn.cursor()

# # cria a tabela (schema) de leituras
# cursor.execute("""
#     CREATE TABLE leituras (
#         data DATE,
#         local CHAR(20),
#         tensao NUMERIC(3,1),
#         temperatura NUMERIC(2,1),
#         humidade NUMERIC(3),
#         choveAgora BOOLEAN
#     )
# """)

# print('Tabela criada com sucesso!')

# # desconecta do banco de dados
# conn.close()

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado no Broker MQTT!")
        else:
            print("Falha na conexão! Codigo: %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Recebido '{msg.payload.decode()}' do tópico '{msg.topic}'")
        
        pub = msg.payload.decode()
        local = 'Estrela Sul'
        tensao = float(pub)
        temp = None
        hum = None
        chove = None

        conn = sqlite3.connect('leiturasEsp32.db')
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO leituras (data, local, tensao, temperatura, humidade, choveAgora)
        VALUES (?,?,?,?,?,?)
        """, (datetime.now(), local, tensao, temp, hum, chove))

        conn.commit()
        print('Dados persistidos!')
        conn.close()

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()