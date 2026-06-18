# admin_app.py - Separate Admin Application on Port 5001
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, User, Category, Product, BlogPost, Review, AffiliateClick, Order, OrderItem
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import re
import random
import string
import os
import secrets
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'admin-secret-key-different-from-main'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///affiliate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads'
PRODUCT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'products')
BLOG_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'blog')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PRODUCT_UPLOAD_FOLDER'] = PRODUCT_UPLOAD_FOLDER
app.config['BLOG_UPLOAD_FOLDER'] = BLOG_UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Create upload folders if they don't exist
os.makedirs(PRODUCT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, folder, slug, max_size=(800, 800)):
    """Save image with resizing"""
    if file and allowed_file(file.filename):
        # Generate random filename
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(file.filename)
        image_filename = f"{slug}_{random_hex}{f_ext}"
        image_path = os.path.join(folder, image_filename)
        
        # Resize and save image
        img = Image.open(file)
        img.thumbnail(max_size)
        img.save(image_path, optimize=True, quality=85)
        
        return image_filename
    return None

def delete_image(filepath):
    """Delete an image file"""
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ==================== CREATE ADMIN USER ====================

def create_admin_user():
    """Create admin user if it doesn't exist"""
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@affiliate.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            return True
        else:
            print("✅ Admin user already exists")
            return True
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

# ==================== ADMIN LOGIN ====================

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Welcome to Admin Panel!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Access denied.', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

# ==================== ADMIN DASHBOARD ====================

@app.route('/')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    total_products = Product.query.count()
    total_categories = Category.query.count()
    total_blogs = BlogPost.query.count()
    total_reviews = Review.query.count()
    total_users = User.query.count()
    total_clicks = AffiliateClick.query.count()
    total_orders = Order.query.count()
    
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_categories=total_categories,
                         total_blogs=total_blogs,
                         total_reviews=total_reviews,
                         total_users=total_users,
                         total_clicks=total_clicks,
                         total_orders=total_orders,
                         recent_products=recent_products,
                         recent_users=recent_users,
                         recent_orders=recent_orders)

# ==================== ADMIN PRODUCTS ====================

@app.route('/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    products = pagination.items
    
    return render_template('admin/products.html', products=products, pagination=pagination)

@app.route('/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        original_price = request.form.get('original_price')
        affiliate_link = request.form.get('affiliate_link')
        image_icon = request.form.get('image_icon')
        rating = float(request.form.get('rating'))
        category_id = int(request.form.get('category_id'))
        commission_rate = float(request.form.get('commission_rate'))
        is_trending = 'is_trending' in request.form
        is_featured = 'is_featured' in request.form
        
        # Handle image upload
        image_url = request.form.get('image_url')
        image_file = None
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                image_file = save_image(file, PRODUCT_UPLOAD_FOLDER, slug, (800, 800))
        
        if Product.query.filter_by(slug=slug).first():
            flash('Slug already exists!', 'error')
            categories = Category.query.all()
            return render_template('admin/add_product.html', categories=categories)
        
        product = Product(
            name=name, slug=slug, description=description, price=price,
            original_price=float(original_price) if original_price else None,
            affiliate_link=affiliate_link, image_icon=image_icon, rating=rating,
            category_id=category_id, commission_rate=commission_rate,
            is_trending=is_trending, is_featured=is_featured,
            image_url=image_url, image_file=image_file
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.slug = request.form.get('slug')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.original_price = float(request.form.get('original_price')) if request.form.get('original_price') else None
        product.affiliate_link = request.form.get('affiliate_link')
        product.image_icon = request.form.get('image_icon')
        product.rating = float(request.form.get('rating'))
        product.category_id = int(request.form.get('category_id'))
        product.commission_rate = float(request.form.get('commission_rate'))
        product.is_trending = 'is_trending' in request.form
        product.is_featured = 'is_featured' in request.form
        product.image_url = request.form.get('image_url')
        product.updated_at = datetime.utcnow()
        
        # Handle image upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # Delete old image if exists
                if product.image_file:
                    delete_image(os.path.join(PRODUCT_UPLOAD_FOLDER, product.image_file))
                product.image_file = save_image(file, PRODUCT_UPLOAD_FOLDER, product.slug, (800, 800))
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_product(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        product = Product.query.get_or_404(id)
        product_name = product.name
        
        # Delete associated image file if exists
        if product.image_file:
            delete_image(os.path.join(PRODUCT_UPLOAD_FOLDER, product.image_file))
        
        db.session.delete(product)
        db.session.commit()
        
        print(f"✅ Product '{product_name}' (ID: {id}) deleted successfully")
        return jsonify({'success': True, 'message': f'Product "{product_name}" deleted'})
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting product: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ADMIN CATEGORIES ====================

@app.route('/categories')
@login_required
def admin_categories():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/category/add', methods=['GET', 'POST'])
@login_required
def admin_add_category():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        icon = request.form.get('icon')
        description = request.form.get('description')
        display_order = int(request.form.get('display_order'))
        
        if Category.query.filter_by(slug=slug).first():
            flash('Slug already exists!', 'error')
            return render_template('admin/add_category.html')
        
        category = Category(
            name=name, slug=slug, icon=icon, 
            description=description, display_order=display_order
        )
        db.session.add(category)
        db.session.commit()
        
        flash('Category added!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_category(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        category.icon = request.form.get('icon')
        category.description = request.form.get('description')
        category.display_order = int(request.form.get('display_order'))
        
        db.session.commit()
        flash('Category updated!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/category/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_category(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    category = Category.query.get_or_404(id)
    if category.products:
        return jsonify({'success': False, 'error': 'Category has products'}), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== ADMIN BLOG ====================

@app.route('/blog')
@login_required
def admin_blog():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    
    return render_template('admin/blog.html', posts=pagination, pagination=pagination)

@app.route('/blog/add', methods=['GET', 'POST'])
@login_required
def admin_add_blog():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        author = request.form.get('author')
        image_icon = request.form.get('image_icon')
        tags = request.form.get('tags')
        is_published = 'is_published' in request.form
        
        # Handle image upload
        image_url = request.form.get('image_url')
        image_file = None
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                image_file = save_image(file, BLOG_UPLOAD_FOLDER, slug, (800, 450))
        
        if BlogPost.query.filter_by(slug=slug).first():
            flash('Slug already exists!', 'error')
            return render_template('admin/add_blog.html')
        
        post = BlogPost(
            title=title, slug=slug, content=content, excerpt=excerpt,
            category=category, author=author, tags=tags,
            image_icon=image_icon, image_url=image_url, image_file=image_file,
            is_published=is_published,
            author_id=current_user.id if current_user else None
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/add_blog.html')

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_blog(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.slug = request.form.get('slug')
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        post.category = request.form.get('category')
        post.author = request.form.get('author')
        post.image_icon = request.form.get('image_icon')
        post.tags = request.form.get('tags')
        post.is_published = 'is_published' in request.form
        post.updated_at = datetime.utcnow()
        
        # Handle image upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # Delete old image if exists
                if post.image_file:
                    delete_image(os.path.join(BLOG_UPLOAD_FOLDER, post.image_file))
                post.image_file = save_image(file, BLOG_UPLOAD_FOLDER, post.slug, (800, 450))
        
        # Update image URL if provided
        post.image_url = request.form.get('image_url')
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/edit_blog.html', post=post)

@app.route('/blog/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_blog(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        post = BlogPost.query.get_or_404(id)
        post_title = post.title
        
        # Delete image if exists
        if post.image_file:
            delete_image(os.path.join(BLOG_UPLOAD_FOLDER, post.image_file))
        
        db.session.delete(post)
        db.session.commit()
        
        print(f"✅ Blog post '{post_title}' (ID: {id}) deleted successfully")
        return jsonify({'success': True, 'message': f'Blog post "{post_title}" deleted'})
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting blog post: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ADMIN USERS ====================

@app.route('/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/user/toggle-admin/<int:id>', methods=['POST'])
@login_required
def admin_toggle_admin(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot change own admin status'})
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/user/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot delete own account'})
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== ADMIN REVIEWS ====================

@app.route('/reviews')
@login_required
def admin_reviews():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/review/approve/<int:id>', methods=['POST'])
@login_required
def admin_approve_review(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    review = Review.query.get_or_404(id)
    review.is_approved = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/review/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_review(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== ADMIN ORDERS ====================

@app.route('/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    orders = pagination.items
    
    # Get order statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='delivered').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status == 'delivered').scalar() or 0
    
    return render_template('admin/orders.html', 
                         orders=pagination, 
                         pagination=pagination,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         total_revenue=total_revenue)

@app.route('/order/view/<int:id>')
@login_required
def admin_view_order(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    order = Order.query.get_or_404(id)
    return render_template('admin/view_order.html', order=order)

@app.route('/order/update-status/<int:id>', methods=['POST'])
@login_required
def admin_update_order_status(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid status'}), 400

# ==================== SETTINGS (Placeholder) ====================

@app.route('/settings')
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/settings.html')

# ==================== RUN APP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user
        create_admin_user()
        
        # Create sample order if none exist
        try:
            if Order.query.count() == 0:
                sample_order = Order(
                    order_number='ORD-' + ''.join(random.choices(string.digits, k=8)),
                    customer_name='John Doe',
                    customer_email='john@example.com',
                    customer_phone='+1234567890',
                    total_amount=299.99,
                    status='pending',
                    payment_status='pending',
                    shipping_address='123 Main St, New York, NY 10001'
                )
                db.session.add(sample_order)
                db.session.commit()
                print("✅ Sample order created")
        except Exception as e:
            print(f"⚠️ Sample order creation skipped: {e}")
    
    print("=" * 50)
    print("🚀 Starting ADMIN PANEL on Port 5001")
    print("=" * 50)
    print("🔐 ADMIN PANEL ACCESS:")
    print("   URL: http://127.0.0.1:5001/login")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5001)