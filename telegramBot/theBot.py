from DBFunctions import DBFunctions
import os.path
import telegram
import redis
import gettext
import configparser
import json
import logging

from telegram.ext import (
    Updater, 
    CommandHandler,
    MessageHandler,
    RegexHandler,
    Filters
)

# Configuração
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Conexão com a API do Telegram
updater = Updater(token=config['DEFAULT']['token'], use_context=True)
dispatcher = updater.dispatcher

# Conexão com o Redis DB
# db = redis.StrictRedis(host=config['DB']['host'],
#                        port=config['DB']['port'],
#                        db=config['DB']['db'])

# Log padrão
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

dados = DBFunctions()


def start(update, context):
    
    chatId = update.effective_chat.id
    
    # print('effective_chat: ', update.effective_chat)
    # print('effective_message: ', update.effective_message)
    # print('effective_user: ', update.effective_user)
    # print('chatId: ', chatId)

    saudacao = ''
    nome = ''

    if update.effective_chat.type == 'group':
        saudacao = 'grupo '
        nome = update.effective_chat.title
    else:
        nome = update.effective_chat.first_name

    texto = "Oi, " + saudacao + nome + "! Eu sou o EnergyBot.\n"
    texto += "\nFui criado como parte do projeto de TCC do Eduardo Ciscoto.\n"
    texto += "Meu objetivo é reunir dados sobre o fornecimento de energia elétrica, "
    texto += "gerados a partir de diferentes pontos da cidade, analisá-los e apresentar "
    texto += "informações sobre a qualidade do fornecimento as pessoas que quiserem interagir comigo.\n"
    texto += "\nEm breve disponibilizarei estas informações em forma de comandos para serem acessadas.\n"
    texto += "\nPor enquanto, estou em fase de desenvolvimento e testes...\n"
    # texto += "\nEnvie /menu para conhecer as informações disponíveis no momento."
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


# Função "Tensão média do dia de hoje"
def tensaoMediaHoje(update, context):
    
    mediaHoje = dados.todaysAvg()[0][0]

    texto = "A média das leituras de tensão feitas hoje é de:\n"
    texto += "" + round(mediaHoje) + "V\n"
    texto += "\nLembro que este valor está arredondado e pode não refletir "
    texto += "a realidade devido a imprecisão dos equipamentos de medição."
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


# Função "Eco" (envia o que recebe)
def echo(update, context):
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = update.message.text
    )


# Trata comandos desconhecidos enviados pelo usuário
def unknown(update, context):
    chatId = update.effective_chat.id
    
    texto = "Desculpe. Não reconheci o comando enviado."
    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Handlers
start_handler = CommandHandler('start', start)
tensaoMediaHoje_handler = CommandHandler('tensaoMediaHoje', tensaoMediaHoje)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
help_handler = CommandHandler('help', start)
unknown_handler = MessageHandler(Filters.command, unknown)

# Passando os Handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(tensaoMediaHoje_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unknown_handler)

# to run this program:
# updater.start_polling()
# to stop it:
# updater.stop()