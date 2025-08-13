from flask import request, jsonify
from config import app
from FastraxPOS import FastraxPOS

# @app.route('/products', methods=['GET'])
# def get_products():
#     products = FastraxPOS.query.all()
#     return jsonify([product.to_json() for product in products])
