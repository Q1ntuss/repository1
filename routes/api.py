from flask import Blueprint, jsonify, request
from models import get_products, add_product, delete_product, get_feedbacks, add_feedback

api = Blueprint('api', __name__)

@api.route('/products', methods=['GET'])
def api_get_products():
    return jsonify({"products": get_products()}), 200

@api.route('/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    product = next((p for p in get_products() if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

@api.route('/products', methods=['POST'])
def api_create_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    add_product(data["name"], data.get("description",""), data["price"], data["stock"])
    return jsonify({"status": "success"}), 201