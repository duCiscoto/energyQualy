from DBFunctions import DBFunctions
from paho.mqtt import client as mqtt_client
import theBot


broker = 'broker.emqx.io'
port = 1883
topic = "tccEngSoftwareECC/Metropolitan"
# monitorar o tópico tccEngSoftwareECC e, para cada sequência, um novo lugar (automático?)

client_id = 'assinanteTcc'
username = ''
password = ''

db = DBFunctions()


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

        leitura = {}
        
        pub = msg.payload.decode()
        # cep = capturar do tópico da publicação
        
        leitura['cep'] = 36030711 #passar sempre inteiro
        leitura['fase1'] = float(pub)
        leitura['fase2'] = None # adicionar publicação no ESP32
        leitura['fase3'] = None # adicionar publicação no ESP32
        leitura['temperatura'] = None # configurar sensor
        leitura['humidade'] = None # configurar sensor
        leitura['chove'] = None # configurar sensor

        print(f"Recebido '{pub}' do tópico '{msg.topic}'")

        variou = db.variouTensao(leitura)
        #variou ainda não funciona
        #dispara mensagens a cada publicação
        
        if variou:
            interessados = db.interessadosCep(leitura['cep'])
            for id in interessados:
                theBot.enviaNotificacao(variou, id[0])
                print('Alerta do CEP {}-{} enviado para chatId {}'.format(
                    str(leitura['cep'])[:5],
                    str(leitura['cep'])[5:],
                    id[0]
                ))


        db.insertLeitura(leitura)

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()