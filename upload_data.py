from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from db import db
import os
import zipfile

# Blueprint for data upload
upload_data_bp = Blueprint('upload_data', __name__, url_prefix='/api/data')

# Data model
class DataFile(db.Model):
    __tablename__ = 'data_files'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

# Allowed file extensions
ALLOWED_EXTENSIONS = { 'bag', 'zip', 'pdf'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload a file


@upload_data_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    title = request.form.get('title')
    description = request.form.get('description')

    if file.filename == '' or not title:
        return jsonify({'error': 'Missing title or file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        upload_folder = current_app.config['UPLOAD_DATA_FOLDER']
        
        # Full path for the saved file
        filepath = os.path.join(upload_folder, filename)

        if file_extension == 'bag':
            # Save the original .bag file temporarily
            temp_filepath = os.path.join(upload_folder, f"temp_{filename}")
            file.save(temp_filepath)

            # Compress the .bag file into a .zip archive
            zip_filename = filename.rsplit('.', 1)[0] + '.zip'
            zip_filepath = os.path.join(upload_folder, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_filepath, arcname=filename)

            # Remove the temporary .bag file
            os.remove(temp_filepath)

            # Update the filepath and filename for saving in the database
            filename = zip_filename
        else:
            # Save the file directly for allowed types other than .bag
            file.save(filepath)

        # Save file metadata to the database
        new_file = DataFile(title=title, description=description, filename=filename)
        db.session.add(new_file)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully', 'file_id': new_file.id}), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400


# Route to get file metadata
@upload_data_bp.route('', methods=['GET'])
def get_files():
    files = DataFile.query.all()
    return jsonify([
        {
            'id': file.id,
            'title': file.title,
            'description': file.description,
            'filename': file.filename,
            'created_at': file.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for file in files
    ])

# Route to download a file
@upload_data_bp.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = DataFile.query.get(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404

    filepath = os.path.join(current_app.config['UPLOAD_DATA_FOLDER'], file.filename)  # Download from correct folder
    return send_file(filepath, as_attachment=True)

# Route to update file metadata
@upload_data_bp.route('/update/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    file = DataFile.query.get(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404

    title = request.json.get('title')
    description = request.json.get('description')

    if title:
        file.title = title
    if description:
        file.description = description

    db.session.commit()
    return jsonify({'message': 'File updated successfully'}), 200

# Route to delete a file
@upload_data_bp.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file = DataFile.query.get(file_id)
    if not file:
        return jsonify({'error': 'File not found'}), 404

    db.session.delete(file)
    db.session.commit()
    # Optionally, remove the file from the filesystem
    filepath = os.path.join(current_app.config['UPLOAD_DATA_FOLDER'], file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    return jsonify({'message': 'File deleted successfully'}), 200
