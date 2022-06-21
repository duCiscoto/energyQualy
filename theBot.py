from DBFunctions import DBFunctions
from datetime import datetime
import configparser
import logging
import telegram
import re

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
            texto += "Fase 3: sem leituras\n"
        texto += "\n* Valores arredondados. Podem não refletir "
        texto += "a realidade devido a imprecisão dos equipamentos de medição."
    else:
        texto = "Lamento. \nAinda não foram realizadas publicações hoje."
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


# Função "Última leitura realizada"
def ultimaLeitura(update, context):

    interacao(update, 'Última leitura')
    chatId = update.effective_chat.id
    texto = ''
    ceps = dados.cepsDoInteressado(chatId)

    if len(ceps) != 0:
        
        for i, c in enumerate(ceps):
            cep = str(c[0])
            leitura = dados.lastEntryCep(cep)
            local = dados.cepMonitorado(cep)

            texto += "{} - {}-{}: {}\n".format(
                i + 1,
                str(local[0][2])[:5],
                str(local[0][2])[5:],
                local[0][3]
            )
        
            data = leitura[0][1].strftime('%d/%m/%Y')
            hora = leitura[0][1].strftime('%H:%M:%S')
            
            texto += "     Última leitura: "
            texto += "{} - {}".format(hora, data)
            
            if leitura[0][3] != None:
                texto += "\n     Fase 1: {}V".format(str(leitura[0][3]).replace('.', ','))
            if leitura[0][4] != None:
                texto += "\n     Fase 2: {}V".format(str(leitura[0][4]).replace('.', ','))
            if leitura[0][5] != None:
                texto += "\n     Fase 3: {}V".format(str(leitura[0][5]).replace('.', ','))
            
            texto += "\n\n"
            
        texto += "* Valores arredondados. Pode não refletir "
        texto += "a realidade devido a imprecisão dos equipamentos de medição."
        
    else:
        texto += 'Sinto muito.\n'
        texto += 'Você ainda não está monitorando nenhum CEP.'



    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Função "Última leitura realizada"
def menu(update, context):

    interacao(update, 'Menu')

    texto = 'Menu de interações\n'
    texto += '\n "/comando": "informação"'
    texto += '\n "/start": boas-vindas;'
    texto += '\n "/ultimaleitura": última leitura nos CEPs monitorados;'
    # texto += '\n /tensaoMediaHoje: média calculada a partir das leituras de hoje até o momento;'
    texto += '\n "/listarceps": lista os CEPs monitorados;'
    texto += '\n "/monitorar #CEP": inicia o monitoramento do CEP;'
    texto += '\n "/abandonar #CEP": deixa de monitorar o CEP;'
    texto += '\n "/menu": interações disponíveis;'
    
    context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = texto
    )


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


# Lista CEPs monitorados
def listarCeps(update, context):

    interacao(update, 'Listar CEPs')
    
    chatId = update.effective_chat.id
    lista = dados.listarCepsMonitorados()
    texto = ''
    
    if len(lista) != 0:
        texto += 'Lista de CEPs monitorados:\n\n'
        for i, local in enumerate(lista):
            texto += '{} - {}-{}: {}\n'.format(
                i + 1,
                str(local[0])[:5],
                str(local[0])[5:],
                local[1]
            )
        texto += '\nPara monitorar um local, envie "/monitorar #CEP".'
    else:
        texto += 'Sinto muito.\n'
        texto += 'Ainda não existem CEPs monitorados.'

    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Cadastra CEP de interesse do usuário
def monitorar(update, context):

    interacao(update, 'Monitorar')
    chatId = update.effective_chat.id
    texto = ''
    
    try:
        c = context.args[0]
        cep = re.sub('[^0-9]', '', c)
        if len(cep):
            if len(dados.cepMonitorado(cep)) != 0:
                if len(dados.interessadoNoCep(chatId, cep)) == 0:
                    dados.insertInteressado(chatId, cep)
                    texto += 'Cadastro realizado com sucesso!\n'
                    texto += 'A partir de agora, se houver grandes oscilações '
                    texto += 'na rede, você será notificado.'
                else:
                    texto += 'Você já está monitorando o CEP fornecido.'
            else:
                texto += 'Ainda não há monitoramento no CEP fornecido.'
        else:
            texto = 'Por favor, digite "/monitorar #CEP"'

    except (IndexError, ValueError):
        texto = 'Por favor, digite "/monitorar #CEP"'
    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Usuário deixa de monitorar o CEP
def abandonar(update, context):

    interacao(update, 'Abandonar')
    chatId = update.effective_chat.id
    texto = ''
    
    try:
        c = context.args[0]
        cep = re.sub('[^0-9]', '', c)
        if len(cep):
            if len(dados.interessadoNoCep(chatId, cep)) != 0:
                dados.deleteInteressado(chatId, cep)
                texto += 'Exclusão realizada com sucesso!\n'
                texto += 'A partir de agora, você não será notificado '
                texto += 'em caso de oscilações na rede.'
            else:
                texto += 'Você não está monitorando o CEP fornecido.'
        else:
            texto = 'Por favor, digite "/abandonar #CEP"'

    except (IndexError, ValueError):
        texto = 'Por favor, digite "/abandonar #CEP"'
    
    context.bot.send_message(
        chat_id = chatId,
        text = texto
    )


# Log no console
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

    agora = datetime.now()
    hora = agora.strftime('%H:%M:%S')
    data = agora.strftime('%d/%m/%Y')

    texto = '\n* * * * * * INTERAÇÃO * * * * * *'
    texto += '\nQuando: {} - {}'.format(hora, data)
    texto += '\nQuem: ' + nome
    texto += '\nO quê: {}'.format(comando)

    print(texto)


# Envia mensagem ao chatId
def enviaNotificacao(msg, chatId):

    bot = telegram.Bot(token=config['DEFAULT']['token'])
    bot.send_message(chat_id=chatId, text=msg)


# Handlers
start_handler = CommandHandler('start', start)
tensaoMediaHoje_handler = CommandHandler('tensaomediahoje', tensaoMediaHoje)
ultima_handler = CommandHandler('ultimaleitura', ultimaLeitura)
menu_handler = CommandHandler('menu', menu)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
help_handler = CommandHandler('help', start)
listarceps_handler = CommandHandler('listarceps', listarCeps)
monitorar_handler = CommandHandler('monitorar', monitorar)
abandonar_handler = CommandHandler('abandonar', abandonar)
unknown_handler = MessageHandler(Filters.command, unknown)

# Passando os Handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(tensaoMediaHoje_handler)
dispatcher.add_handler(ultima_handler)
dispatcher.add_handler(menu_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(listarceps_handler)
dispatcher.add_handler(monitorar_handler)
dispatcher.add_handler(abandonar_handler)
dispatcher.add_handler(unknown_handler)



# to run this program:
# updater.start_polling()
# to stop it:
# updater.stop()