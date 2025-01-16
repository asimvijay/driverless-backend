import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from db import db
from flask_cors import CORS

# Define the blueprint for the blog functionality
blog_bp = Blueprint('blog', __name__, url_prefix='/api/blogs')


# Define the Blog model for the database
class Blog(db.Model):
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    comments = db.relationship('Comment', backref='blog', lazy=True)
    likes = db.relationship('Like', back_populates='blog', lazy=True)

    # Method to count the number of likes
    def count_likes(self):
        return Like.query.filter_by(type='blog', post_id=self.id).count()


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    username = db.Column(db.String(120), nullable=False)

    # Establish foreign key relationship with the Blog table using back_populates
    blog = db.relationship('Blog', back_populates='likes', lazy=True)

    __table_args__ = (db.UniqueConstraint('type', 'post_id', 'username', name='_type_post_user_uc'),)



class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)  # Renamed blog_id to post_id
    username = db.Column(db.String(120), nullable=False)  # New column to store the user ID
    type = db.Column(db.String(50), nullable=False)  # New column to store the type (e.g., 'blog')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

@blog_bp.route('/<int:blog_id>/details', methods=['GET'])
def get_blog_details(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    
    # Print fetched blog details
    print("Fetched Blog:", blog)

    # Fetch comments and likes for the specific blog post
    comments = Comment.query.filter_by(post_id=blog.id).all()
    likes_count = blog.count_likes()

    # Print fetched comments and likes count
    print("Fetched Comments:", comments)
    print("Likes Count:", likes_count)

    # Check if the current user has liked the post (use request args or headers for username)
    username = request.args.get('username')
    liked_by_user = False
    if username:
        liked_by_user = Like.query.filter_by(type='blog', post_id=blog.id, username=username).first() is not None
    
    # Print if the current user has liked the post
    print(f"Liked by user '{username}':", liked_by_user)

    # Construct the response data
    comments_data = [{'id': comment.id, 'content': comment.content, 'username': comment.username} for comment in comments]

    # Print the final response data
    print("Response Data:", {
        'comments': comments_data,
        'likes': likes_count,
        'liked_by_user': liked_by_user
    })

    return jsonify({
        'comments': comments_data,
        'likes': likes_count,
        'liked_by_user': liked_by_user
    }), 200



# Helper function to check allowed extensions
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Route to create a new blog post with image upload
 # Change to your uploads folder

@blog_bp.route('', methods=['POST'])
def create_blog():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the image file

        # Create the blog post
        data = request.form
        new_blog = Blog(
            title=data.get('title'),
            description=data.get('description'),
            image_filename=filename
        )
        db.session.add(new_blog)
        db.session.commit()
        return jsonify({'message': 'Blog created successfully', 'blog': new_blog.id}), 201
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@blog_bp.route('', methods=['GET'])
def get_blogs():
    username = request.args.get('username')
    blogs = Blog.query.all()

    result = []
    for blog in blogs:
        liked = False
        if username:
            liked = Like.query.filter_by(type='blog', post_id=blog.id, username=username).first() is not None

        # Use the count_likes method to get the like count
        likes_count = blog.count_likes()

        result.append({
            'id': blog.id,
            'title': blog.title,
            'description': blog.description,
            'image_url': f"/uploads/{blog.image_filename}" if blog.image_filename else None,
            'likes': likes_count,
            'liked_by_user': liked,
            'comments': [{'id': comment.id, 'content': comment.content} for comment in blog.comments],
            'created_at': blog.created_at
        })

    return jsonify(result), 200




@blog_bp.route('/<int:id>/like', methods=['POST'])
def like_blog(id):
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404

    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'message': 'username is required'}), 400

    # Check if the user has already liked this blog post
    existing_like = Like.query.filter_by(type='blog', post_id=id, username=username).first()
    if existing_like:
        return jsonify({'message': 'You have already liked this blog'}), 400

    # Create a new like record
    new_like = Like(type='blog', post_id=id, username=username)
    db.session.add(new_like)
    db.session.commit()

    # Get the updated like count using the method
    likes_count = blog.count_likes()
    return jsonify({'message': 'Blog liked successfully', 'likes': likes_count}), 200



@blog_bp.route('/<int:id>/comments', methods=['POST'])
def add_comment(id):
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404

    data = request.get_json()
    content = data.get('content')
    username = data.get('username')  # Get the username from the request
    type = 'blog'  # You can change this if you need other types (e.g., 'post')

    if not content or not username:
        return jsonify({'message': 'Comment content and username are required'}), 400

    # Create a new comment with the username and type
    new_comment = Comment(post_id=id, username=username, type=type, content=content)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully', 'comment_id': new_comment.id}), 201


# Route to delete a blog
@blog_bp.route('/<int:id>', methods=['DELETE'])
def delete_blog(id):
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404

    if blog.image_filename:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], blog.image_filename))
        except OSError:
            pass
    
    db.session.delete(blog)
    db.session.commit()
    return jsonify({'message': 'Blog deleted successfully'}), 200

# Route to update a blog post with optional image update
@blog_bp.route('/<int:id>', methods=['PUT'])
def update_blog(id):
    blog = Blog.query.get(id)
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404

    data = request.form
    blog.title = data.get('title', blog.title)
    blog.description = data.get('description', blog.description)

    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if blog.image_filename:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], blog.image_filename))
                except OSError:
                    pass

            blog.image_filename = filename

    db.session.commit()
    return jsonify({'message': 'Blog updated successfully'}), 200