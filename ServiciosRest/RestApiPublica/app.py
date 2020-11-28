from configuracion import getConfigParserGet
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from modelos import Modelo, ModeloSchema
app = Flask(__name__)
db = SQLAlchemy(app)


@app.route('/modelos', methods=['GET'])
def index():
    getModelos = Modelo.query.all()
    modeloSchema = ModeloSchema(many=True)
    modelos = modeloSchema.dump(getModelos)
    return make_response(jsonify({"modelo": modelos}))


@app.route('/modelo/<id>', methods=['GET'])
def getModeloById(id):
    getModelo = Modelo.query.get(id)
    modeloSchema = ModeloSchema()
    modelo = modeloSchema.dump(getModelo)
    return make_response(jsonify({"modelo": modelo}))


if __name__ == "__main__":
    confConexion = 'mysql+pymysql://'
    confConexion = confConexion + getConfigParserGet('bddUser')
    confConexion = confConexion + ':' + getConfigParserGet('bddPassword')
    confConexion = confConexion + '@' + getConfigParserGet('bddHost')
    confConexion = confConexion + ':' + getConfigParserGet('bddPort')
    confConexion = confConexion + '/' + getConfigParserGet('bddDatabase')
    app.config['SQLALCHEMY_DATABASE_URI'] = confConexion
    app.run(debug=True)
