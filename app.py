from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
# pip install -U Flask-SQLAlchemy
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
STATIC_FOLDER = "static/posts/images"
app.config['UPLOAD_FOLDER'] = STATIC_FOLDER
db.__init__(app)

# Pages:
@app.route('/contactus',endpoint='contactus')
def contactus():
    return render_template('posts/contactus.html')
@app.route('/aboutus',endpoint='aboutus')
def aboutus():
    return render_template('posts/aboutus.html')
# ------------------------------------------------

class Post(db.Model):
    STATIC_FOLDER = "posts/images"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    image = db.Column(db.String)
    body = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def get_image_url(self):
        return url_for('static', filename=f'{self.STATIC_FOLDER}/{self.image}')
    
    @property
    def get_show_url(self):
        return url_for('post.detials', id=self.id)
    
    @property
    def get_delete_url(self):
        return url_for('post.delete', id=self.id)
    
    @property
    def get_edit_url(self):
        return url_for('post.edit', id=self.id)
# ------------------------------------------------

    
# Home Page : All Posts
@app.route('/',endpoint='posts')
def posts():
    posts = Post.query.all()
    return render_template('posts/posts.html',posts=posts)

# Add New Post
@app.route('/add_new_post', endpoint='post.add', methods=['GET', 'POST'])
def addnewpost():
    if request.method == 'POST':
        post = Post(title=request.form['title'], image=request.files['image'], body=request.form['body'])
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                if post.image: # if image exists 
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                file.save(file_path)
                post.image = filename
        db.session.add(post)
        db.session.commit()
        return redirect(post.get_show_url)
    return render_template('posts/addnewpost.html')

# Post details Page
@app.route('/post/<int:id>', endpoint='post.detials')
def post_details(id):
    post = Post.query.get_or_404(id)
    if post:
        return render_template('posts/posts_details.html',post=post)
    else:
        return '<h1> Object not found </h1>', 404

# Delete Post 
@app.route('/post/<int:id>/delete', endpoint='post.delete')
def post_delete(id):
    post = Post.query.get_or_404(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('posts'))

# Edit Post
@app.route('/post/<int:id>/edit', endpoint='post.edit', methods=['GET', 'POST'])
def editpost(id):
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.image = request.files['image']
        post.body = request.form['body']
        if 'image' in request.files:
            file = request.files['image']
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                if post.image: # if image exists 
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                file.save(file_path)
                post.image = filename
        db.session.commit()
        return redirect(post.get_show_url)
    return render_template('posts/editpost.html', post=post)

@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return  render_template('errors/page_not_found.html')

if __name__ == '__main__':
    app.run(debug=True)
