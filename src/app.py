"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from models import Favorites_Types
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Favorites_Types, People, Planet
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize()for user in users]), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "El usuario no existe"}), 404
    return jsonify(user.serialize()), 200


@app.route('/planet', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize()for planet in planets]), 200


@app.route('/people', methods=['GET'])
def get_all_peoples():
    peoples = People.query.all()
    return jsonify([unaPersona.serialize()for unaPersona in peoples]), 200


@app.route('/favorite/<string:fav_type>/<int:item_id>', methods=['POST'])
def add_favorite(fav_type, item_id):
    body = request.get_json()
    user_id = body.get("user_id")

    if not user_id:
        return jsonify({"msg": "user_id es requerido"}), 400

    if fav_type == "people":
        person = People.query.get(item_id)
        if not person:
            return jsonify({"msg": "Persona no encontrada"}), 404

        existing = Favorites.query.filter_by(
            user_id=user_id, people_id=item_id).first()
        if existing:
            return jsonify({"msg": "Ya está en favoritos"}), 409

        fav = Favorites(
            type=Favorites_Types.people,
            user_id=user_id,
            people_id=item_id
        )

    elif fav_type == "planet":
        planet = Planet.query.get(item_id)
        if not planet:
            return jsonify({"msg": "Planeta no encontrado"}), 404

        existing = Favorites.query.filter_by(
            user_id=user_id, planet_id=item_id).first()
        if existing:
            return jsonify({"msg": "Ya está en favoritos"}), 409

        fav = Favorites(
            type=Favorites_Types.planet,
            user_id=user_id,
            planet_id=item_id
        )

    else:
        return jsonify({"msg": "Tipo de favorito no válido"}), 400

    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Favorito agregado", "favorite": fav.serialize()}), 201


@app.route('/favorite/<string:fav_type>/<int:item_id>', methods=['DELETE'])
def delete_favorite(fav_type, item_id):
    body = request.get_json()
    user_id = body.get("user_id")

    if not user_id:
        return jsonify({"msg": "user_id es requerido"}), 400

    if fav_type == "people":
        fav = Favorites.query.filter_by(
            user_id=user_id, people_id=item_id).first()
    elif fav_type == "planet":
        fav = Favorites.query.filter_by(
            user_id=user_id, planet_id=item_id).first()
    else:
        return jsonify({"msg": "Tipo de favorito no válido"}), 400

    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorito eliminado"}), 200



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
