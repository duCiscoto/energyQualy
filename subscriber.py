from DBFunctions import DBFunctions
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "tccEngSoftwareECC/Metropolitan"

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
        
        pub = msg.payload.decode()
        place = 'Estrela Sul'
        tensao = float(pub)
        temperatura = None
        umidade = None
        chove = None

        print(f"Recebido '{msg.payload.decode()}' do tópico '{msg.topic}'")
        
        db.insertLeitura(
            place, tensao, temperatura, umidade, chove
        )

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()