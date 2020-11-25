from __future__ import print_function
import pickle
import os
import io
import shutil
import configparser
import logging
import telebot
import mysql.connector
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
            ruta = obtenerRuta(carpetaDrive.get('id'), False)
            if ruta not in dicCarpetas.keys():
                dicCarpetas[ruta] = [carpetaDrive]
            else:
                dicCarpetas[ruta].append(carpetaDrive)
        except:
            logging.error("Error al buscar la ruta de %s" % carpetaDrive)

    logging.info("Aniadiendo elementos de Drive...")

    marcarModelosAntiguos()

    for i in sorted(dicCarpetas.keys()):
        dicCarpetasOrdenadas = {}
        for k in dicCarpetas[i]:
            dicCarpetasOrdenadas[k.get('name')] = k.get('id')

        for j in sorted(dicCarpetasOrdenadas.keys()):
            imagen = None
            imagenEncontrada = False
            response = buscarDrive(
                '(mimeType != \'application/vnd.google-apps.folder\') and (trashed = false) and (\'' + dicCarpetasOrdenadas[j] + '\' in parents)')
            ficheros = response.get('files', [])

            enlaces = []
            for file in ficheros:
                nombre = file.get('name')
                if '.PNG' in nombre or '.png' in nombre or '.JPEG' in nombre or '.jpeg' in nombre or '.jpg' in nombre or '.JPG' in nombre and imagenEncontrada is False:
                    ficheroGdrive = getDriveService().files().get(fileId=file.get('id'), fields="webContentLink").execute()
                    imagen = ficheroGdrive['webContentLink'].replace('&export=download', '')
                    darPermisosLectura(file.get('id'))
                    imagenEncontrada = True
                if '.URL' in nombre or '.url' in nombre:
                    enlace = getEnlaceFicheroUrl(file.get('id'))
                    if enlace:
                        enlaces.append(enlace)

            modeloRuta = obtenerRuta(dicCarpetasOrdenadas[j], True)
            modeloId = insertModelo(getNombreLimpio(j), imagen, modeloRuta)
            enlaces.append("https://drive.google.com/open?id=%s" % (dicCarpetasOrdenadas[j]))
            for enlace in enlaces:
                insertEnlace(modeloId, enlace)

            rutas = modeloRuta.split('/')
            rutas.remove(rutas[0])
            rutas.remove(rutas[0])
            for etiqueta in rutas:
                insertEtiqueta(modeloId, etiqueta)

    eliminarModelosAntiguos()

    getConexion().commit()
    getCursor().close()
    getConexion().close()
    enviarMensajeTelegram(getConfigParserGet('telegramMensaje'))


def eliminarModelosAntiguos():
    queryDeleteEnlaces = "DELETE FROM enlaces WHERE ID_MODELO IN (SELECT ID FROM modelos WHERE ANTERIOR = 1)"
    queryDeleteEtiquetasAsociadas = "DELETE FROM modelo_x_etiqueta WHERE ID_MODELO IN (SELECT ID FROM modelos WHERE ANTERIOR = 1)"
    queryDeleteModelos = "DELETE FROM modelos WHERE ANTERIOR = 1"
    getCursor().execute(queryDeleteEnlaces)
    getCursor().execute(queryDeleteEtiquetasAsociadas)
    getCursor().execute(queryDeleteModelos)


def marcarModelosAntiguos():
    queryUpdate = "UPDATE modelos SET ANTERIOR = 1 WHERE ANTERIOR = 0"
    getCursor().execute(queryUpdate)


def insertEnlace(modeloId, enlace):
    queryGetIdWeb = "SELECT ID FROM webs_enlaces WHERE NOMBRE = %s"
    queryInsertWeb = "INSERT INTO webs_enlaces(WEB, NOMBRE) VALUES(%s, %s)"
    queryInsertEnlace = "INSERT INTO enlaces(ID_MODELO, ID_WEB, ENLACE) SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT ENLACE FROM enlaces WHERE ENLACE = %s)"

    idWebEncontrado = None
    nombreWeb = getNombreWeb(enlace)
    getCursor().execute(queryGetIdWeb, (nombreWeb, ))
    for (id) in getCursor():
        idWebEncontrado = id[0]

    if idWebEncontrado is None:
        getCursor().execute(queryInsertWeb, (getEnlaceWeb(enlace), nombreWeb))
        idWebEncontrado = getCursor().lastrowid

    getCursor().execute(queryInsertEnlace, (modeloId, idWebEncontrado, enlace, enlace))


def getNombreWeb(enlace):
    return enlace.replace('https://', '').replace('http://', '').replace('www.', '').split("/")[0]


def getEnlaceWeb(enlace):
    splitWeb = enlace.split("/")
    return "%s//%s" % (splitWeb[0], splitWeb[2])


def insertModelo(nombreMod, imagen, enlaceDriveMod):
    queryInsert = "INSERT INTO modelos(NOMBRE, IMG, PATH_DRIVE, ANTERIOR) VALUES(%s, %s, %s, 0) ON DUPLICATE KEY UPDATE IMG = %s, PATH_DRIVE = %s, FECHA_MODIF = NOW(), ANTERIOR = 0"
    queryGetId = "SELECT ID FROM modelos WHERE NOMBRE = %s"

    getCursor().execute(queryInsert, (nombreMod, imagen, enlaceDriveMod, imagen, enlaceDriveMod))
    modeloId = getCursor().lastrowid
    if modeloId is None:
        for (id) in getCursor():
            modeloId = id

    return modeloId


def insertEtiqueta(modeloId, nuevaEtiqueta):
    queryInsertEtiqueta = "INSERT INTO etiquetas(ETIQUETA) SELECT %s FROM DUAL WHERE NOT EXISTS (SELECT ETIQUETA FROM etiquetas WHERE ETIQUETA = %s)"
    queryGetIdEtiqueta = "SELECT ID FROM etiquetas WHERE ETIQUETA = %s"
    queryInsertModeloEtiqueta = "INSERT INTO modelo_x_etiqueta(ID_MODELO, ID_ETIQUETA) SELECT %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM modelo_x_etiqueta WHERE ID_MODELO = %s AND ID_ETIQUETA = %s)"
    getCursor().execute(queryInsertEtiqueta, (nuevaEtiqueta, nuevaEtiqueta))
    getCursor().execute(queryGetIdEtiqueta, (nuevaEtiqueta, ))
    resultado = getCursor()
    for (id) in resultado:
        etiquetaId = id[0]

    getCursor().execute(queryInsertModeloEtiqueta, (modeloId, etiquetaId, modeloId, etiquetaId))


def getEnlaceFicheroUrl(id):
    try:
        resultado = None
        ficheroUrl = getDriveService().files().get_media(fileId=id)
        ficheroBytes = io.BytesIO()
        ficheroDescarga = MediaIoBaseDownload(ficheroBytes, ficheroUrl)
        descargado = False
        while descargado is False:
            descargado = ficheroDescarga.next_chunk()

        ficheroBytes.seek(0)
        ficheroCompleto = ficheroBytes.read().decode("utf-8")
        ficheroBytes.close()
        if 'InternetShortcut' in ficheroCompleto:
            comienzoUrl = ficheroCompleto.index('URL=')
            finUrl = ficheroCompleto.index('IDList=')
            resultado = ficheroCompleto[comienzoUrl + 4:finUrl - 2]

        return resultado
    except:
        logging.error("Error al recuperar el enlace de %s" % id)


def darPermisosLectura(id):
    try:
        getDriveService().permissions().create(
            body={"role": "reader", "type": "anyone"}, fileId=id).execute()
    except:
        logging.error("Error al asignar permisos a %s" % id)


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
            if contador >= 10 and modoPrueba:
                break
        pageToken = response.get('nextPageToken', None)
        if pageToken is None or modoPrueba:
            logging.info("Se han encontrado %s carpetas con \' by \'" % len(carpetasDrive))
            break
    return carpetasDrive


def obtenerRuta(idCarpeta, completo):
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
            if completo is False and folder.get('name') in str(getCatEsp()):
                return folder.get('name')

            tree.append(folder.get('name'))

    tree.reverse()
    length = len(tree)
    ruta = ''
    for i in range(length):
        if (i == 1 and completo is False) or completo is True:
            ruta = ruta + '/' + tree[i]

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


def getNombreLimpio(nombre=None):
    return re.sub(r"[^a-zA-Z0-9 .]", "", nombre)


def getCatEsp():
    global categoriasEspeciales
    if categoriasEspeciales is None:
        categoriasEspeciales = getConfigParserGet('categoriasEspeciales')
    return categoriasEspeciales


def enviarMensajeTelegram(mensaje):
    telegramBotToken = getConfigParserGet('telegramBotToken')
    telegramChatId = getConfigParserGet('telegramChatId')
    telegramMensaje = getConfigParserGet('telegramMensaje')

    if(telegramBotToken and telegramChatId):
        telegramService = telebot.TeleBot(telegramBotToken)
        telegramService.send_message(telegramChatId, mensaje)


if __name__ == '__main__':
    main()
