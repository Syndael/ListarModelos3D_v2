from __future__ import print_function
import pickle
import os
import configparser
import logging
import telebot
import mysql.connector
import random

lectorConfig = None
conexion = None
cursor = None


def main():
    ficheroLog = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'listar.log')
    logging.basicConfig(filename=ficheroLog, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

    print(insertEtiqueta("Test " + str(random.randint(0, 9999))))
    print(insertEtiqueta("Test 1"))

    getConexion().commit()
    getCursor().close()
    getConexion().close()

    """ enviarMensajeTelegram('test') """


def insertEtiqueta(nuevaEtiqueta):
    queryInsert = "INSERT INTO etiquetas(ETIQUETA) SELECT (%s) FROM DUAL WHERE NOT EXISTS (SELECT ETIQUETA FROM etiquetas WHERE ETIQUETA = %s)"
    queryGetId = "SELECT ID FROM etiquetas WHERE ETIQUETA = %s"
    getCursor().execute(queryInsert, (nuevaEtiqueta, nuevaEtiqueta))
    return getCursor().execute(queryGetId, (nuevaEtiqueta, ))


def getConexion():
    global conexion
    if conexion is None:
        conexion = mysql.connector.connect(user=getConfigParserGet('bddUser'), password=getConfigParserGet(
            'bddPassword'), host=getConfigParserGet('bddHost'), database=getConfigParserGet('bddDatabase'), port=getConfigParserGet('bddPort'))

    return conexion


def getCursor():
    global cursor
    if cursor is None:
        cursor = getConexion().cursor()

    return cursor


def getConfigParserGet(clave):
    return getConfigParser().get('config', clave)


def getConfigParser():
    global lectorConfig
    if lectorConfig is None:
        lectorConfig = configparser.RawConfigParser()
        ficheroConfig = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.txt')
        lectorConfig.read(ficheroConfig)

    return lectorConfig


def enviarMensajeTelegram(urlFichero):
    telegramBotToken = getConfigParserGet('telegramBotToken')
    telegramChatId = getConfigParserGet('telegramChatId')
    telegramMensaje = getConfigParserGet('telegramMensaje')

    if(telegramBotToken and telegramChatId):
        telegramService = telebot.TeleBot(telegramBotToken)
        mensaje = 'OK'
        if(telegramMensaje):
            mensaje = telegramMensaje.replace('[url]', urlFichero)

        telegramService.send_message(telegramChatId, mensaje)


if __name__ == '__main__':
    main()
