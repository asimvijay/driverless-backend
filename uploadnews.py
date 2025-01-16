from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from db import db  # Import the single db instance from models.py

# Initialize blueprint for upload-related routes
upload_bp = Blueprint('upload', __name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model for storing post data
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_url = db.Column(db.String(255), nullable=False)  # Generic media URL
    media_type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    caption = db.Column(db.String(255), nullable=True)
    subtitle = db.Column(db.String(), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "media_url": self.media_url,
            "media_type": self.media_type,
            "caption": self.caption,
            "subtitle": self.subtitle
        }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve static files (uploaded media)
@upload_bp.route('/uploads/<filename>')
def serve_media(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route to upload media and store post data in the database
@upload_bp.route('/api/post', methods=['POST'])
def post_media():
    if 'file' not in request.files:  # Change 'media' to 'file'
        return jsonify({"error": "No file part"}), 400

    media = request.files['file']  # Change 'media' to 'file'
    
    if media.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if media and allowed_file(media.filename):
        filename = secure_filename(media.filename)
        media_path = os.path.join(UPLOAD_FOLDER, filename)
        media.save(media_path)

        media_url = f'http://localhost:5000/uploads/{filename}'
        media_type = 'video' if media.content_type.startswith('video/') else 'image'
        
        caption = request.form.get('caption')
        subtitle = request.form.get('subtitle')

        # Save to database
        new_post = Post(media_url=media_url, media_type=media_type, caption=caption, subtitle=subtitle)
        db.session.add(new_post)
        db.session.commit()

        return jsonify(new_post.to_dict()), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400


# Route to get all posts from the database
@upload_bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])

# Route to update a post by ID
@upload_bp.route('/api/post/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get(id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    # Check if a new file is being uploaded
    if 'file' in request.files:
        media = request.files['file']
        if media and allowed_file(media.filename):
            filename = secure_filename(media.filename)
            media_path = os.path.join(UPLOAD_FOLDER, filename)
            media.save(media_path)

            post.media_url = f'http://localhost:5000/uploads/{filename}'
            post.media_type = 'video' if media.content_type.startswith('video/') else 'image'

    caption = request.form.get('caption')
    subtitle = request.form.get('subtitle')

    if caption:
        post.caption = caption
    if subtitle:
        post.subtitle = subtitle

    db.session.commit()
    return jsonify(post.to_dict()), 200


# Route to delete a post by ID
@upload_bp.route('/api/post/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return '', 204
