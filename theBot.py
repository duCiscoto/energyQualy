from DBFunctions import DBFunctions
from datetime import datetime, date
import configparser
import logging

from telegram.ext import (
    Updater, 
    CommandHandler,
    MessageHandler,
    Filters
)

# Configuração
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Conexão com a API do Telegram
updater = Updater(
    token = config['DEFAULT']['token'],
    use_context = True
)
dispatcher = updater.dispatcher

# Log padrão
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

dados = DBFunctions()


def start(update, context):

    interacao(update, 'Start')
    
    chatId = update.effective_chat.id
    
    saudacao = ''
    nome = ''

    if update.effective_chat.type == 'group':
        saudacao = ' pessoal do grupo '
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
    texto += "\nEnvie /menu para conhecer as informações disponíveis até o momento."
    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Função "Tensão média do dia de hoje"
def tensaoMediaHoje(update, context):

    interacao(update, 'Tensão média hoje')
    
    mediaHoje = dados.todaysAvg()

    texto = "Tensão média de hoje (até o momento)\n"

    if mediaHoje[0][3] != 0:
        texto += "\nQuantidade de leituras: " + str(mediaHoje[0][3]) + "\n"
        if mediaHoje[0][0] != None:
            texto += "Fase 1: " + str(round(mediaHoje[0][0])) + "V *\n"
        else:
            texto += "Fase 1: sem leituras\n"
        if mediaHoje[0][1] != None:
            texto += "Fase 2: " + str(round(mediaHoje[0][1])) + "V *\n"
        else:
            texto += "Fase 2: sem leituras\n"
        if mediaHoje[0][2] != None:
            texto += "Fase 3: " + str(round(mediaHoje[0][2])) + "V *\n"
        else:
            texto += "Fase 3: sem leituras até o momento\n"
        texto += "\n* Valores arredondados. Podem não refletir "
        texto += "a realidade devido a imprecisão dos equipamentos de medição."
    else:
        texto = "Lamento. \nAinda não foram realizadas publicações hoje."
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


# Função "Última leitura realizada"
def agora(update, context):

    interacao(update, 'Última leitura')

    leitura = dados.now()
    # formatado = agora[0][1].strftime('%d/%m/%Y'), agora[0][1].strftime('%H:%M:%S'), agora[0][3]
    data = leitura[0][1].strftime('%d/%m/%Y')
    hora = leitura[0][1].strftime('%H:%M:%S')
    
    texto = "Última leitura realizada às "
    texto += "{} de".format(hora)
    texto += " {}\n".format(data)
    if leitura[0][3] != None:
        texto += "\nFase 1: {}V".format(str(leitura[0][3]).replace('.', ','))
    else:
        texto += "\nFase 1: sem leitura"
    if leitura[0][4] != None:
        texto += "\nFase 2: {}V".format(str(leitura[0][4]).replace('.', ','))
    else:
        texto += "\nFase 2: sem leitura"
    if leitura[0][5] != None:
        texto += "\nFase 3: {}V\n".format(str(leitura[0][5]).replace('.', ','))
    else:
        texto += "\nFase 3: sem leitura\n"
    texto += "\n* Valores arredondados. Pode não refletir "
    texto += "a realidade devido a imprecisão dos equipamentos de medição."
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


# Função "Última leitura realizada"
def menu(update, context):

    interacao(update, 'Menu')

    texto = 'Menu de informações\n'
    texto += '\n"/comando": "informação"'
    texto += '\n /start: boas-vindas;'
    texto += '\n /agora: última leitura realizada;'
    texto += '\n /tensaoMediaHoje: média calculada a partir das leituras de hoje até o momento;'
    texto += '\n /menu: informações disponíveis;'
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )

    # interacao(update, context)


# Função "Eco" (envia o que recebe)
def echo(update, context):

    interacao(update, 'Eco')
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = update.message.text
    )


# Trata comandos desconhecidos enviados pelo usuário
def unknown(update, context):

    interacao(update, 'Comando desconhecido')
    
    chatId = update.effective_chat.id
    
    texto = "Desculpe. Não reconheci o comando enviado."
    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


def interacao(update, comando):

    nome = ''

    if update.effective_chat.type == 'group':
        nome = '{} {}'.format(
            'Grupo',
            update.effective_chat.title
        )
    elif update.effective_chat.type == 'private':
        nome = '{} {}'.format(
            update.effective_chat.first_name,
            update.effective_chat.last_name
        )
    else:
        nome = 'Tipo do destinatário desconhecido'

    # chatId = 1023606093 # meu!

    agora = datetime.now()
    hora = agora.strftime('%H:%M:%S')
    data = agora.strftime('%d/%m/%Y')

    texto = '\n * * * * * INTERAÇÃO * * * * * '
    texto += '\nQuando: {} - {}'.format(hora, data)
    texto += '\nQuem: ' + nome
    texto += '\nO quê: ' + comando
    texto += '\n * * * * * * * * * * * * * * *'

    print(texto)


# Handlers
start_handler = CommandHandler('start', start)
tensaoMediaHoje_handler = CommandHandler('tensaoMediaHoje', tensaoMediaHoje)
agora_handler = CommandHandler('agora', agora)
menu_handler = CommandHandler('menu', menu)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
help_handler = CommandHandler('help', start)
unknown_handler = MessageHandler(Filters.command, unknown)

# Passando os Handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(tensaoMediaHoje_handler)
dispatcher.add_handler(agora_handler)
dispatcher.add_handler(menu_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unknown_handler)



# to run this program:
# updater.start_polling()
# to stop it:
# updater.stop()