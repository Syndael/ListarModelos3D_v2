from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Modelo(db.Model):
    __tablename__ = 'modelos'

    id = db.Column(db.Integer(), primary_key=True)
    nombre = db.Column(db.String(127))
    img = db.Column(db.String(255))
    path_drive = db.Column(db.String(255))
    anterior = db.Column(db.Boolean())
    fecha_ins = db.Column(db.DateTime())
    fecha_modif = db.Column(db.DateTime())

    def __init__(self, nombre, img, path_drive, anterior, fecha_ins, fecha_modif):
        self.nombre = nombre
        self.img = img
        self.path_drive = path_drive
        self.anterior = anterior
        self.fecha_ins = fecha_ins
        self.fecha_modif = fecha_modif

    def json(self):
        return {"nombre": self.nombre, "img": self.img, "path_drive": self.path_drive, "anterior": self.anterior, "fecha_ins": self.fecha_ins, "fecha_modif": self.fecha_modif}


class ModeloSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Modelo
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    nombre = fields.String(required=True)
    img = fields.String(required=False)
    path_drive = fields.String(required=False)
    anterior = fields.Boolean(required=True)
    fecha_ins = fields.DateTime(required=True)
    fecha_modif = fields.DateTime(required=True)


class Enlace(db.Model):
    __tablename__ = 'enlaces'

    id = db.Column(db.Integer(), primary_key=True)
    id_modelo = db.Column(db.Integer(), ForeignKey("modelos.id"))
    id_web = db.Column(db.Integer())
    enlace = db.Column(db.String(255))

    modelo = relationship("Modelo", foreign_keys=[id_modelo])

    def __init__(self, id_modelo, id_web, enlace, modelo):
        self.id_modelo = id_modelo
        self.id_web = id_web
        self.enlace = enlace
        self.modelo = modelo

    def json(self):
        return {"id_modelo": self.id_modelo, "id_web": self.id_web, "enlace": self.enlace, "modelo": self.modelo}


class EnlaceSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        enlace = Enlace
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    id_modelo = fields.Number(required=True)
    id_web = fields.Number(required=False)
    enlace = fields.String(required=True)
