from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models import db, User, Category, Product, BlogPost, Review, AffiliateClick, UserProductView, NewsletterSubscriber, SiteSettings
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
import re
import json
import secrets
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
# app.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///affiliate.db')
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

# Custom filter for datetime
@app.template_filter('datetime')
def format_datetime(value, format='%B %d, %Y'):
    """Format a datetime or return current date"""
    if value == "now":
        return datetime.now().strftime(format)
    return value.strftime(format) if value else ""

# ==================== CONTEXT PROCESSOR ====================

@app.context_processor
def inject_categories():
    """Make categories and request available in all templates"""
    categories = Category.query.order_by(Category.display_order).all()
    return dict(all_categories=categories, request=request)

# ==================== SAMPLE DATA INITIALIZATION ====================

def init_sample_data():
    """Create sample categories, products, blog posts and reviews"""
    
    # Check if already populated
    if Category.query.first():
        return
    
    print("Creating sample data...")
    
    # Create categories
    categories_data = [
        ('Gadgets & Tech', 'gadgets-tech', 'fas fa-microchip', 'Latest electronics, headphones, laptops & smart devices', 1),
        ('Wellness & Self-care', 'wellness-selfcare', 'fas fa-heartbeat', 'Self-care tools, meditation aids, wellness gadgets', 2),
        ('Home & Living', 'home-living', 'fas fa-home', 'Cozy decor, kitchen essentials, smart home devices', 3),
        ('Photography', 'photography', 'fas fa-camera', 'Cameras, lenses, accessories for creators', 4),
        ('Fashion & Accessories', 'fashion-accessories', 'fas fa-tshirt', 'Streetwear, jewelry, bags & style essentials', 5),
        ('Fitness Gear', 'fitness-gear', 'fas fa-dumbbell', 'Equipment, smart trackers, activewear', 6),
        ('Digital Courses', 'digital-courses', 'fas fa-graduation-cap', 'Online learning, guides & templates', 7),
        ('Art & Stationery', 'art-stationery', 'fas fa-paintbrush', 'Journals, pens, art supplies, planners', 8),
    ]
    
    categories = []
    for name, slug, icon, desc, order in categories_data:
        cat = Category(name=name, slug=slug, icon=icon, description=desc, display_order=order)
        db.session.add(cat)
        categories.append(cat)
    db.session.commit()
    
    # Create sample products
    products_by_category = {
        'gadgets-tech': [
            ('Sony WH-1000XM5 Headphones', 'sony-wh1000xm5', 'Premium noise-cancelling headphones with exceptional sound quality.', 348, 399, 'https://amzn.to/sample1', 'fas fa-headphones', 4.9, 1240, True, True, 15),
            ('Apple MacBook Air M2', 'macbook-air-m2', 'Supercharged by the next-generation M2 chip.', 1099, 1299, 'https://amzn.to/sample2', 'fas fa-laptop', 4.8, 856, True, True, 12),
            ('AirPods Pro 2', 'airpods-pro-2', 'Active noise cancellation and spatial audio.', 199, 249, 'https://amzn.to/sample3', 'fas fa-headphones', 4.9, 3420, True, False, 10),
            ('Samsung Galaxy Watch 6', 'galaxy-watch-6', 'Advanced health tracking and fitness monitoring.', 289, 349, 'https://amzn.to/sample4', 'fas fa-clock', 4.7, 892, True, False, 12),
            ('Logitech MX Master 3S', 'mx-master-3s', 'Ultra-fast scrolling and ergonomic design.', 89, 109, 'https://amzn.to/sample5', 'fas fa-mouse', 4.8, 2100, False, True, 8),
        ],
        'wellness-selfcare': [
            ('Aromatherapy Diffuser', 'aroma-diffuser', 'Ultrasonic essential oil diffuser.', 29.99, 49.99, 'https://amzn.to/sample6', 'fas fa-spa', 4.7, 340, True, True, 12),
            ('Meditation Cushion', 'meditation-cushion', 'Zafu meditation pillow.', 45, 69, 'https://amzn.to/sample7', 'fas fa-lotus', 4.8, 230, True, False, 10),
            ('Weighted Blanket', 'weighted-blanket', '15lbs glass bead weighted blanket.', 79, 129, 'https://amzn.to/sample8', 'fas fa-bed', 4.6, 890, True, True, 8),
        ],
    }
    
    for cat in categories:
        cat_products = products_by_category.get(cat.slug, [])
        for name, slug, desc, price, orig_price, link, icon, rating, reviews, trending, featured, comm in cat_products:
            product = Product(
                name=name, slug=slug, description=desc, price=price, original_price=orig_price,
                affiliate_link=link, image_icon=icon, rating=rating, reviews_count=reviews,
                category_id=cat.id, is_trending=trending, is_featured=featured, commission_rate=comm
            )
            db.session.add(product)
    db.session.commit()
    
    # Create blog posts with images
    blog_posts = [
        ('Why Pastel Niches Convert Better in 2026', 'why-pastel-niches-convert', 'Learn how aesthetic affiliate marketing boosts trust and sales.', 'Strategy', 'Sarah Johnson', 'fas fa-chart-line', 'pastel-niches.jpg'),
        ('10 High-Ticket Affiliate Programs', 'high-ticket-affiliate-programs', 'Discover the most profitable affiliate programs.', 'Tips & Tricks', 'Mike Chen', 'fas fa-dollar-sign', 'high-ticket.jpg'),
        ('SEO Secrets for Product Reviews', 'seo-product-reviews', 'A complete blueprint to rank your affiliate reviews.', 'SEO', 'Emma Watson', 'fas fa-magnifying-glass', 'seo-secrets.jpg'),
        ('How to Build an Email List', 'build-email-list', 'Learn effective strategies to grow your email subscriber list.', 'Email Marketing', 'David Brown', 'fas fa-envelope', 'email-list.jpg'),
        ('Affiliate Marketing for Beginners', 'affiliate-beginners', 'Step by step guide to start your affiliate marketing journey.', 'Beginners', 'Lisa Wong', 'fas fa-rocket', 'affiliate-beginners.jpg'),
    ]
    
    for title, slug, excerpt, category, author, icon, img in blog_posts:
        content = f"""
        <h2>Introduction</h2>
        <p>{excerpt}</p>
        <h2>Key Takeaways</h2>
        <ul>
            <li>Understanding the current market trends</li>
            <li>Actionable strategies for immediate implementation</li>
            <li>Expert tips to maximize your results</li>
        </ul>
        <h2>Deep Dive</h2>
        <p>This comprehensive guide covers everything you need to know about {title.lower()}.</p>
        <h2>Conclusion</h2>
        <p>Implement these strategies today and watch your affiliate income grow!</p>
        """
        post = BlogPost(
            title=title, slug=slug, excerpt=excerpt, content=content,
            category=category, author=author, image_icon=icon,
            image_file=img,  # Sample image filename
            tags='affiliate, marketing, tips, strategy'
        )
        db.session.add(post)
    db.session.commit()
    
    # Create sample reviews
    reviews_data = [
        ('Jessica Miller', 'JM', 5, 'Absolutely love these headphones! The noise cancellation is incredible.', 1),
        ('David Kim', 'DK', 4, 'Great product but a bit pricey. Still worth it for the quality.', 2),
        ('Sarah Williams', 'SW', 5, 'Life-changing! The meditation cushion improved my daily practice significantly.', 3),
        ('Michael Brown', 'MB', 5, 'The MacBook Air M2 is a beast! Super fast and battery lasts all day.', 2),
        ('Emily Davis', 'ED', 4, 'Very comfortable weighted blanket. Helps me sleep better at night.', 3),
        ('Chris Wilson', 'CW', 5, 'Best investment I made this year. Highly recommend!', 1),
    ]
    
    for name, avatar, rating, comment, prod_id in reviews_data:
        review = Review(user_name=name, user_avatar=avatar, rating=rating, comment=comment, product_id=prod_id, is_approved=True)
        db.session.add(review)
    db.session.commit()
    
    # Create admin user
    admin = User(username='admin', email='admin@affiliate.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    
    db.session.commit()
    
    print("=" * 50)
    print("✅ Sample data created successfully!")
    print("=" * 50)
    print("🔐 ADMIN ACCESS ONLY:")
    print("   Admin Login URL: http://127.0.0.1:5000/admin-panel/login")
    print("   Username: admin")
    print("   Password: admin123")
    print("-" * 50)
    print("👥 CUSTOMER ACCESS (No Login Required):")
    print("   Customer Site URL: http://127.0.0.1:5000/")
    print("=" * 50)

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    trending_products = Product.query.filter_by(is_trending=True).limit(12).all()
    latest_blog = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(4).all()
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(8).all()
    categories = Category.query.order_by(Category.display_order).all()
    
    return render_template('index.html', 
                         trending_products=trending_products,
                         latest_blog=latest_blog,
                         reviews=reviews,
                         categories=categories)

@app.route('/categories')
def all_categories():
    categories = Category.query.order_by(Category.display_order).all()
    
    categories_with_counts = []
    for cat in categories:
        product_count = Product.query.filter_by(category_id=cat.id).count()
        categories_with_counts.append({
            'category': cat,
            'product_count': product_count
        })
    
    return render_template('all_categories.html', categories=categories_with_counts)

@app.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    pagination = Product.query.filter_by(category_id=category.id).paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    return render_template('category.html', 
                         category=category, 
                         products=products,
                         pagination=pagination)

@app.route('/product/<slug>')
def product(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).all()
    related = Product.query.filter_by(category_id=product.category_id).filter(Product.id != product.id).limit(4).all()
    
    return render_template('product.html', 
                         product=product, 
                         reviews=reviews, 
                         related=related)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    
    return render_template('blog.html', posts=pagination, pagination=pagination)

@app.route('/blog/<slug>')
def blog_post(slug):
    try:
        post = BlogPost.query.filter_by(slug=slug).first()
        
        if not post:
            flash('Blog post not found!', 'error')
            return redirect(url_for('blog'))
        
        # Increment views
        post.views += 1
        db.session.commit()
        
        # Get related posts
        related_posts = BlogPost.query.filter(
            BlogPost.category == post.category, 
            BlogPost.id != post.id,
            BlogPost.is_published == True
        ).limit(3).all()
        
        return render_template('blog_post.html', post=post, related_posts=related_posts)
        
    except Exception as e:
        print(f"❌ Error in blog_post: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading blog post', 'error')
        return redirect(url_for('blog'))

@app.route('/reviews')
def reviews_page():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    pagination = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    reviews = pagination.items
    
    all_reviews = Review.query.filter_by(is_approved=True).all()
    avg_rating = 0
    if all_reviews:
        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    
    return render_template('reviews.html', 
                         reviews=pagination, 
                         pagination=pagination,
                         avg_rating=avg_rating,
                         total_reviews=len(all_reviews))

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('index'))
    
    products = Product.query.filter(
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    posts = BlogPost.query.filter(
        db.or_(
            BlogPost.title.ilike(f'%{query}%'),
            BlogPost.content.ilike(f'%{query}%'),
            BlogPost.excerpt.ilike(f'%{query}%')
        ),
        BlogPost.is_published == True
    ).limit(10).all()
    
    total_results = len(products) + len(posts)
    
    return render_template('search.html', 
                         query=query, 
                         products=products, 
                         posts=posts,
                         total_results=total_results)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/affiliate-disclosure')
def affiliate_disclosure():
    return render_template('affiliate_disclosure.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# ==================== API ROUTES ====================

@app.route('/api/click/<int:product_id>', methods=['POST'])
def track_click(product_id):
    product = Product.query.get(product_id)
    if product:
        click = AffiliateClick(
            product_id=product_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            referrer=request.referrer
        )
        db.session.add(click)
        product.click_count = (product.click_count or 0) + 1
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'affiliate_link': product.affiliate_link
        })
    
    return jsonify({'success': False}), 404

@app.route('/api/review/helpful/<int:review_id>', methods=['POST'])
def review_helpful(review_id):
    review = Review.query.get_or_404(review_id)
    review.helpful_count = (review.helpful_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True, 'count': review.helpful_count})

# ==================== ADMIN LOGIN ====================

@app.route('/admin-panel/login', methods=['GET', 'POST'])
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

@app.route('/admin-panel/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

# ==================== ADMIN DASHBOARD ====================

@app.route('/admin-panel')
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
    
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_categories=total_categories,
                         total_blogs=total_blogs,
                         total_reviews=total_reviews,
                         total_users=total_users,
                         total_clicks=total_clicks,
                         recent_products=recent_products,
                         recent_users=recent_users)

# ==================== ADMIN PRODUCTS ====================

@app.route('/admin-panel/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    products = pagination.items
    
    return render_template('admin/products.html', products=products, pagination=pagination)

@app.route('/admin-panel/product/add', methods=['GET', 'POST'])
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

@app.route('/admin-panel/product/edit/<int:id>', methods=['GET', 'POST'])
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
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # Delete old image
                if product.image_file:
                    delete_image(os.path.join(PRODUCT_UPLOAD_FOLDER, product.image_file))
                product.image_file = save_image(file, PRODUCT_UPLOAD_FOLDER, product.slug, (800, 800))
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin-panel/product/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_product(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    product = Product.query.get_or_404(id)
    
    if product.image_file:
        delete_image(os.path.join(PRODUCT_UPLOAD_FOLDER, product.image_file))
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_products'))

# ==================== ADMIN CATEGORIES ====================

@app.route('/admin-panel/categories')
@login_required
def admin_categories():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin-panel/category/add', methods=['GET', 'POST'])
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

@app.route('/admin-panel/category/edit/<int:id>', methods=['GET', 'POST'])
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

@app.route('/admin-panel/category/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_category(id):
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    category = Category.query.get_or_404(id)
    if category.products:
        flash('Cannot delete category with products!', 'error')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted!', 'success')
    return redirect(url_for('admin_categories'))

# ==================== ADMIN BLOG ====================

@app.route('/admin-panel/blog')
@login_required
def admin_blog():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    
    return render_template('admin/blog.html', posts=pagination, pagination=pagination)

@app.route('/admin-panel/blog/add', methods=['GET', 'POST'])
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
        tags = request.form.get('tags')
        is_published = 'is_published' in request.form
        
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
            image_url=image_url, image_file=image_file,
            is_published=is_published,
            author_id=current_user.id if current_user else None
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/add_blog.html')

@app.route('/admin-panel/blog/edit/<int:id>', methods=['GET', 'POST'])
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

@app.route('/admin-panel/blog/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_blog(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    post = BlogPost.query.get_or_404(id)
    
    # Delete image if exists
    if post.image_file:
        delete_image(os.path.join(BLOG_UPLOAD_FOLDER, post.image_file))
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== ADMIN USERS ====================

@app.route('/admin-panel/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin-panel/user/toggle-admin/<int:id>', methods=['POST'])
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

@app.route('/admin-panel/user/delete/<int:id>', methods=['POST'])
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

@app.route('/admin-panel/reviews')
@login_required
def admin_reviews():
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('admin_login'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin-panel/review/approve/<int:id>', methods=['POST'])
@login_required
def admin_approve_review(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    review = Review.query.get_or_404(id)
    review.is_approved = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin-panel/review/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_review(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    
    return jsonify({'success': True})

# ==================== DEBUG ROUTES ====================

@app.route('/debug-routes')
def debug_routes():
    """Show all registered routes"""
    html = "<h1>All Routes</h1><ul>"
    for rule in app.url_map.iter_rules():
        html += f"<li><code>{rule}</code></li>"
    html += "</ul>"
    html += "<p><a href='/'>Go Home</a></p>"
    return html

@app.route('/debug-posts')
def debug_posts():
    """Show all blog posts"""
    posts = BlogPost.query.all()
    if not posts:
        return "<h1>No posts found!</h1><p><a href='/'>Go Home</a></p>"
    
    html = "<h1>All Blog Posts</h1><ul>"
    for p in posts:
        html += f"""
        <li>
            <strong>{p.title}</strong><br>
            Slug: <code>{p.slug}</code><br>
            Image: {p.image_file or 'None'}<br>
            Views: {p.views}<br>
            Published: {p.is_published}<br>
            <a href='/blog/{p.slug}'>View Post</a>
        </li>
        <br>
        """
    html += "</ul>"
    html += "<p><a href='/'>Go Home</a></p>"
    return html

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== RUN APP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    print("=" * 50)
    print("🚀 Starting Affiliate Marketplace Server...")
    print("=" * 50)
    print("📝 Main Routes:")
    print("   http://127.0.0.1:5000/")
    print("   http://127.0.0.1:5000/blog")
    print("   http://127.0.0.1:5000/blog/why-pastel-niches-convert")
    print("   http://127.0.0.1:5000/debug-posts")
    print("   http://127.0.0.1:5000/debug-routes")
    print("-" * 50)
    print("🔐 Admin Access:")
    print("   http://127.0.0.1:5000/admin-panel/login")
    print("   Username: admin")
    print("   Password: admin123")
    print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)