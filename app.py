# from flask import Flask
# from flask_cors import CORS
# from db import db
# import os
# from uploadnews import upload_bp
# from uploadProducts import product_bp
# from blog import blog_bp
# from upload_data import upload_data_bp  # Ensure this import

# app = Flask(__name__)
# CORS(app)

# # Folder configurations
# UPLOAD_FOLDER = 'uploads/'
# UPLOAD_DATA_FOLDER = 'upload-data/'  # For data uploads specifically
# BLOGS = 'BLOG'
# PRODUCT_UPLOAD_FOLDER = 'product_uploads/'

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['UPLOAD_DATA_FOLDER'] = UPLOAD_DATA_FOLDER  # Correct folder for data uploads
# app.config['PRODUCT_UPLOAD_FOLDER'] = PRODUCT_UPLOAD_FOLDER
# app.config['BLOGS'] = BLOGS

# # Database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:sSUwVFEK52mH@ep-tiny-morning-a8f8ygw9.eastus2.azure.neon.tech/neondb?sslmode=require"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Initialize the database
# db.init_app(app)

# # Register all blueprints
# app.register_blueprint(upload_bp)
# app.register_blueprint(product_bp)
# app.register_blueprint(blog_bp)
# app.register_blueprint(upload_data_bp)  # Register data upload blueprint

# if __name__ == '__main__':
#     # Ensure upload directories exist
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#     os.makedirs(BLOGS, exist_ok=True)
#     os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)
#     os.makedirs(UPLOAD_DATA_FOLDER, exist_ok=True)  # Create the upload-data folder

#     # Create tables in the database
#     with app.app_context():
#         db.create_all()

#     app.run(debug=True)
from flask import Flask
from flask_cors import CORS
from db import db
import os
from uploadnews import upload_bp
from uploadProducts import product_bp
from blog import blog_bp
from upload_data import upload_data_bp

app = Flask(__name__)
CORS(app)

# Folder configurations
UPLOAD_FOLDER = 'uploads/'
UPLOAD_DATA_FOLDER = 'upload-data/'
BLOGS = 'BLOG'
PRODUCT_UPLOAD_FOLDER = 'product_uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_DATA_FOLDER'] = UPLOAD_DATA_FOLDER
app.config['PRODUCT_UPLOAD_FOLDER'] = PRODUCT_UPLOAD_FOLDER
app.config['BLOGS'] = BLOGS

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:sSUwVFEK52mH@ep-tiny-morning-a8f8ygw9.eastus2.azure.neon.tech/neondb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Register all blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(product_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(upload_data_bp)

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BLOGS, exist_ok=True)
os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_DATA_FOLDER, exist_ok=True)
