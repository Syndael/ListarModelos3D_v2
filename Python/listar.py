from __future__ import print_function
import pickle
import os
import shutil
import configparser
import logging
import telebot
import mysql.connector
import random
import urllib
import mimetypes
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import date
from httplib2 import Http
from oauth2client import client, file, tools
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

lectorConfig = None
conexion = None
cursor = None
driveService = None
categoriasEspeciales = None


def main():
    ficheroLog = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'listar.log')
    logging.basicConfig(filename=ficheroLog, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

    carpetasDrive = buscarCarpetasDrive()
    dicCarpetas = {}
    logging.info("Recuperando rutas de Drive")
    for carpetaDrive in carpetasDrive:
        try:
            ruta = obtenerRuta(carpetaDrive.get('id'), 1)
            if ruta not in dicCarpetas.keys():
                dicCarpetas[ruta] = [carpetaDrive]
            else:
                dicCarpetas[ruta].append(carpetaDrive)
        except:
            logging.error("Error al buscar la ruta de %s" % carpetaDrive)

    logging.info("Aniadiendo elementos de Drive...")

    for i in sorted(dicCarpetas.keys()):
        dicCarpetasOrdenadas = {}
        for k in dicCarpetas[i]:
            dicCarpetasOrdenadas[k.get('name')] = k.get('id')

        for j in sorted(dicCarpetasOrdenadas.keys()):
            enlaceDrive = "https://drive.google.com/open?id=%s" % (dicCarpetasOrdenadas[j])
            logging.info("Path del %s: %s" %
                         (dicCarpetasOrdenadas[j], obtenerRuta(dicCarpetasOrdenadas[j], 99)))

    getConexion().commit()
    getCursor().close()
    getConexion().close()


def getNombreLimpio(nombre=None):
    return re.sub(r"[^a-zA-Z0-9 .]", "", nombre)


def insertModelo(nombreMod, enlaceDriveMod):
    queryInsert = "INSERT INTO modelos(NOMBRE, IMG, PATH_DRIVE) SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT ID FROM modelos WHERE NOMBRE = %s)"
    queryGetId = "SELECT ID FROM modelos WHERE NOMBRE = %s"

    getCursor().execute(queryInsert, (nombreMod, None, enlaceDriveMod, nombreMod))
    nuevoId = getCursor().lastrowid
    if(nuevoId is None):
        return getCursor().execute(queryGetId, (nombreMod, ))

    return nuevoId


def insertEtiqueta(nuevaEtiqueta):
    queryInsert = "INSERT INTO etiquetas(ETIQUETA) SELECT (%s) FROM DUAL WHERE NOT EXISTS (SELECT ETIQUETA FROM etiquetas WHERE ETIQUETA = %s)"
    queryGetId = "SELECT ID FROM etiquetas WHERE ETIQUETA = %s"
    getCursor().execute(queryInsert, (nuevaEtiqueta, nuevaEtiqueta))
    nuevoId = getCursor().lastrowid
    if(nuevoId is None):
        return getCursor().execute(queryGetId, (nuevaEtiqueta, ))

    return nuevoId


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


def buscarCarpetasDrive():
    carpetasDrive = []
    pageToken = None
    modoPrueba = getConfigParserGet('modoPrueba') == "yes"
    while True:
        logging.info("Leyendo carpetas con \' by \'")
        response = buscarDrive(
            '(mimeType = \'application/vnd.google-apps.folder\') and (trashed = false) and fullText contains \'" by "\'', pageToken)
        contador = 0
        for file in response.get('files', []):
            carpetasDrive.append(file)
            contador = contador + 1
            if contador >= 5 and modoPrueba:
                break
        pageToken = response.get('nextPageToken', None)
        if pageToken is None or modoPrueba:
            logging.info("Se han encontrado %s carpetas con \' by \'" % len(carpetasDrive))
            break
    return carpetasDrive


def obtenerRuta(idCarpeta, rango):
    tree = []
    file = getDriveService().files().get(fileId=idCarpeta, fields='id, name, parents').execute()
    parent = file.get('parents')
    if parent:
        while True:
            folder = getDriveService().files().get(
                fileId=parent[0], fields='id, name, parents').execute()
            parent = folder.get('parents')
            if parent is None:
                break

            # Si el nombre de la carpeta esta contenido en la list del conf entonces se devuelve
            if folder.get('name') in str(getCatEsp()):
                return folder.get('name')
            tree.append(folder.get('name'))

    tree.reverse()
    length = len(tree)
    ruta = ''
    for i in range(length):
        if i == rango:
            ruta = ruta + tree[i]

    return ruta


def buscarDrive(filtroQ, pageToken=None):
    return getDriveService().files().list(q=filtroQ, spaces='drive',
                                          fields='nextPageToken, files(id, name)', pageToken=pageToken).execute()


def getDriveService():
    global driveService
    if driveService is None:
        rutaCreedenciales = getConfigParserGet('rutaCreedenciales')
        clienteSecreto = getConfigParserGet('clienteSecreto')
        store = file.Storage(rutaCreedenciales)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(clienteSecreto, SCOPES)
            creds = tools.run_flow(flow, store)
        driveService = build('drive', 'v3', cache_discovery=False, http=creds.authorize(Http()))

    return driveService


def getCatEsp():
    global categoriasEspeciales
    if categoriasEspeciales is None:
        categoriasEspeciales = getConfigParserGet('categoriasEspeciales')
    return categoriasEspeciales


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
