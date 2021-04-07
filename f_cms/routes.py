from operator import pos
from flask import render_template, flash, redirect, url_for, request, abort
from f_cms import app, db, bcrypt, mail
from f_cms.forms import UserRegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from f_cms.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import secrets
import os
from PIL import Image

@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', title='Home', posts=posts)

@app.route('/password', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Sign in unsuccessful', 'danger')
    return render_template('login.html', title='Password', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.username.data}!', 'success')
        return redirect('users')
    users = User.query.all()
    return render_template('users.html', title='Users', form=form, users=users)

@app.route('/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted.', 'success')
    return redirect(url_for('users'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (256, 256)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
        os.remove(prev_picture)

    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

def save_post_img(form_post_img):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_post_img.filename)
    post_img_fn = random_hex + f_ext
    post_img_path = os.path.join(app.root_path, 'static/post_images', post_img_fn)
    form_post_img.save(post_img_path)

    output_size = (1920, 1080)
    i = Image.open(form_post_img)
    i.thumbnail(output_size)
    i.save(post_img_path)

    return post_img_fn

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    posts = Post.query.order_by(Post.date_posted.desc()).all()

    return render_template('posts.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, title_image=form.title_image.data, image_1=form.image_1.data, image_2=form.image_2.data, image_3=form.image_3.data, image_4=form.image_4.data, image_5=form.image_5.data, image_6=form.image_6.data, author=current_user)
        if form.title_image.data:
            title_image_file = save_post_img(form.title_image.data)
            post.title_image = title_image_file
        if form.image_1.data:
            image_1_file = save_post_img(form.image_1.data)
            post.image_1 = image_1_file
        if form.image_2.data:
            image_2_file = save_post_img(form.image_2.data)
            post.image_2 = image_2_file
        if form.image_3.data:
            image_3_file = save_post_img(form.image_3.data)
            post.image_3 = image_3_file
        if form.image_4.data:
            image_4_file = save_post_img(form.image_4.data)
            post.image_4 = image_4_file
        if form.image_5.data:
            image_5_file = save_post_img(form.image_5.data)
            post.image_5 = image_5_file
        if form.image_6.data:
            image_6_file = save_post_img(form.image_6.data)
            post.image_6 = image_6_file
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    
    caption = 'Create a new Post.'
    return render_template('settings_post.html', title='New Post', form=form, legend='New Post', caption=caption)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.title_image.data:
            title_image_file = save_post_img(form.title_image.data)
            post.title_image = title_image_file
        if form.image_1.data:
            image_1_file = save_post_img(form.image_1.data)
            post.image_1 = image_1_file
        if form.image_2.data:
            image_2_file = save_post_img(form.image_2.data)
            post.image_2 = image_2_file
        if form.image_3.data:
            image_3_file = save_post_img(form.image_3.data)
            post.image_3 = image_3_file
        if form.image_4.data:
            image_4_file = save_post_img(form.image_4.data)
            post.image_4 = image_4_file
        if form.image_5.data:
            image_5_file = save_post_img(form.image_5.data)
            post.image_5 = image_5_file
        if form.image_6.data:
            image_6_file = save_post_img(form.image_6.data)
            post.image_6 = image_6_file
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    caption = 'Update your post.'
    return render_template('settings_post.html', title='Update Post', form=form, legend='Update Post', caption=caption)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    title_image = post.title_image
    title_image_path = os.path.join(app.root_path, 'static/post_images', title_image)
    os.remove(title_image_path)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then ignore this email.
'''

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an ivalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has benn updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)