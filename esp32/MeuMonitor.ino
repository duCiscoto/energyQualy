#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define LED 2
#define DHTPIN 12
#define DHTTYPE DHT11

// CONSTANTES DE CONFIGURAÇÃO MQTT (Broker IoTicos.org)
const char *mqttServidor = "broker.emqx.io";
const int mqttPorta = 1883;
const char *mqttUsuario = "";
const char *mqttSenha = "";
const char *rootTopicoInscricao = "tccEngSoftwareECC/input";
const char *rootTopicoPublicacao = "tccEngSoftwareECC/Teste";

// CONSTANTES DE CONFIGURAÇÃO WIFI
const char* ssid = "BelaVista2";
const char* password = "@Ciscoto1110Show";

// VARIÁVEIS GLOBAIS
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

char msg[200];
//float fase1[4];
//float fase2[4];
//float fase3[4];
float medida[4];
String medidas;
//byte porta;

// FUNÇÕES
void callback(char* topic, byte* payload, unsigned int length);
void reconnectMqtt();
void setupWifi();
void mqttConectado();
void mqttDesconectado();

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  setupWifi();
  client.setServer(mqttServidor, mqttPorta);
  client.setCallback(callback);

  pinMode(LED,OUTPUT);

  dht.begin();

}

void loop()
{
  if (!client.connected()) {
    reconnectMqtt();
  }

  if (client.connected())
  {
    getVoltage();

    String medidas = String(medida[2]);
    
//    String medidas = "{'local': 'Estrela Sul', 'fase': " + String(medida[2])
//                   + ", 'temperatura': 0, 'humidade': 50, 'choveAgora': False}";
    
//    String medidas = "{{" + String(fase1[0]) + "," + String(fase2[0]) + "," + String(fase3[0]) + "},"
//                    + "{" + String(fase1[1]) + "," + String(fase2[1]) + "," + String(fase3[1]) + "},"
//                    + "{" + String(fase1[2]) + "," + String(fase2[2]) + "," + String(fase3[2]) + "},"
//                    + "{" + String(fase1[3]) + "," + String(fase2[3]) + "," + String(fase3[3]) + "}}";
    medidas.toCharArray(msg, 200);
    client.publish(rootTopicoPublicacao, msg);
    
//    delay(250);
  }

  mqttConectado();
  
  delay(1000);
//  client.loop();
}

// SETUP WIFI
void setupWifi()
{
  delay(10);
  // Conectando a rede WiFi
  Serial.println();
  Serial.print("Conectando a rede: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectMqtt()
{
  while (!client.connected())
  {
    Serial.println("Tentando conexão MQTT...");

    // Cria um cliente ID
    String clientId = "TCC_ESP32_Metropolitan";
    //clientId += String(random(0xffff), HEX);

    // Tenta conectar
    if (client.connect(clientId.c_str(), mqttUsuario, mqttSenha))
    {
      Serial.println("Conectado!");
      // Inscrevendo no tópico
      if (client.subscribe(rootTopicoInscricao)) {
        Serial.println("Inscrição feita!");
      } else {
        Serial.println("Falha na inscrição");
      }
    } else {
      Serial.print("Houve uma falha. Erro: ");
      Serial.print(client.state());
      Serial.println("; Nova tentativa em 5 segundos.");
    }
    mqttDesconectado();
  }
}

// CALLBACK
void callback(char* topico, byte* payload, unsigned int length)
{
  String incoming = "";
  Serial.print("Mensagem recebida de: ");
  Serial.print(topico);
  Serial.println();
  for (int i = 0; i < length; i++) {
    incoming += (char)payload[i];
  }
  incoming.trim();
  Serial.println("Mensagem: " + incoming);
}

// LEITURA DA TENSÃO
void getVoltage()
{
//  unsigned long x = 0;
//  unsigned long y = 0;
  unsigned long z = 0;
//  x = analogRead(porta);
//  for (int i = 0; i < 5; i++) {
//    x += analogRead(32);
//  }
//  for (int i = 0; i < 5; i++) {
//    y += analogRead(33);
//  }
  for (int i = 0; i < 200; i++) {
    z += analogRead(34);
  }

//  x /= 5;
//  y /= 5;
  z /= 200;

//  medida[0] = (0.0770975056689342 * x + 25) - 44.5;
//  medida[1] = (0.0770975056689342 * y + 25) - 44.5;
  medida[2] = (0.0770975056689342 * z + 25) - 39.5;
  if (medida[2] < 0){
    medida[2] = 0;
  }

//  Serial.print(x);
//  Serial.print("\t");
//  Serial.print(y);
//  Serial.print("\t");
  Serial.println(z);

  Serial.println("medida");
//  Serial.print(medida[0]);
//  Serial.print("\t");
//  Serial.print(medida[1]);
//  Serial.print("\t");
  Serial.println(medida[2]);
  Serial.println("");
//  Serial.println((0.0811594203 * x + 26.2) - 57);

//  return float((0.0811594203 * x + 26.2) - 57);
}

// LED PISCA A CADA PUBLICAÇÃO
void mqttConectado()
{
  digitalWrite(LED, HIGH);
  delay(10);
  digitalWrite(LED, LOW);
  //  delay(500); dispensável pois respeita o delay(1000) no loop()
}

// LED INTERMITENTE QUANDO DESCONECTADO
void mqttDesconectado()
{
  int repete = 5;
  while (repete != 0)
  {
    digitalWrite(LED, HIGH);
    delay(500);
    digitalWrite(LED, LOW);
    delay(500);
    repete -= 1;
  }
}
