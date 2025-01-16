from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from db import db  # Import the single db instance from models.py

# Initialize blueprint for product-related routes
product_bp = Blueprint('product', __name__)

# Folder to store uploaded product images
PRODUCT_UPLOAD_FOLDER = 'product_uploads/'

# Model for storing product data
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "name": self.name,
            "description": self.description
        }

# (Other routes remain unchanged)


# Serve static files (uploaded product images)
@product_bp.route('/product_uploads/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_UPLOAD_FOLDER, filename)


# Route to upload a product image and store product data in the database
@product_bp.route('/api/product', methods=['POST'])
def post_product():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(PRODUCT_UPLOAD_FOLDER, filename)
        image.save(image_path)

        image_url = f'http://localhost:5000/product_uploads/{filename}'
        name = request.form.get('name')
        description = request.form.get('description')

        # Save to database
        new_product = Product(image_url=image_url, name=name, description=description)
        db.session.add(new_product)
        db.session.commit()

        return jsonify(new_product.to_dict()), 201

# Route to get all products from the database
@product_bp.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

# Route to update a product by ID
@product_bp.route('/api/product/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    name = request.form.get('name')
    description = request.form.get('description')

    if name:
        product.name = name
    if description:
        product.description = description

    db.session.commit()
    return jsonify(product.to_dict()), 200

# Route to delete a product by ID
@product_bp.route('/api/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return '', 204
