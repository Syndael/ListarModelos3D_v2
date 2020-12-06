from configuracion import getConfigParserGet
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from modelos import Modelo, ModeloSchema
app = Flask(__name__)


@app.route('/modelos', methods=['GET', 'POST'])
def index():
    start = int(request.args.get('start', 1))
    limit = int(request.args.get('limit', getConfigParserGet('itemsPage')))

    modelosPage = Modelo.query.paginate(start, limit, True, None)
    getModelos = modelosPage.items
    modeloSchema = ModeloSchema(many=True)
    modelos = modeloSchema.dump(getModelos)
    return make_response(jsonify(getJsonPaginado(modelos, modelosPage.total, start, limit)))


@app.route('/modelo/<id>', methods=['GET'])
def getModeloById(id):
    getModelo = Modelo.query.get(id)
    modeloSchema = ModeloSchema()
    modelo = modeloSchema.dump(getModelo)
    return make_response(jsonify({"modelo": modelo}))


def getJsonPaginado(items, total, start, limit):
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = total
    obj['items'] = items
    return obj


if __name__ == "__main__":
    confConexion = 'mysql+pymysql://'
    confConexion = confConexion + getConfigParserGet('bddUser')
    confConexion = confConexion + ':' + getConfigParserGet('bddPassword')
    confConexion = confConexion + '@' + getConfigParserGet('bddHost')
    confConexion = confConexion + ':' + getConfigParserGet('bddPort')
    confConexion = confConexion + '/' + getConfigParserGet('bddDatabase')
    app.config['SQLALCHEMY_DATABASE_URI'] = confConexion
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    app.run(host='0.0.0.0', port=int(getConfigParserGet('appPort')))
