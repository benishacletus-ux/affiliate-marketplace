from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products_viewed = db.relationship('UserProductView', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fas fa-tag')
    description = db.Column(db.String(300))
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    affiliate_link = db.Column(db.String(500), nullable=False)
    image_icon = db.Column(db.String(50), default='fas fa-tag')
    
    # Image fields
    image_url = db.Column(db.String(500))
    image_file = db.Column(db.String(200))
    
    rating = db.Column(db.Float, default=4.5)
    reviews_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_trending = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    commission_rate = db.Column(db.Float, default=10.0)
    click_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    clicks = db.relationship('AffiliateClick', backref='product', lazy=True, cascade='all, delete-orphan')
    views = db.relationship('UserProductView', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def get_discounted_percentage(self):
        if self.original_price and self.original_price > 0:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return round(discount)
        return 0
    
    def get_image_url(self):
        if self.image_file:
            return f'/static/uploads/products/{self.image_file}'
        elif self.image_url:
            return self.image_url
        return None


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    
    # Image fields for blog
    image_file = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    image_icon = db.Column(db.String(50), default='fas fa-newspaper')  # ← ADDED THIS
    
    category = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    author = db.Column(db.String(100))  # Fallback author name
    views = db.Column(db.Integer, default=0)
    read_time = db.Column(db.Integer, default=5)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    author_user = db.relationship('User', backref='authored_posts', foreign_keys=[author_id])
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
    def get_image_url(self):
        if self.image_file:
            return f'/static/uploads/blog/{self.image_file}'
        elif self.image_url:
            return self.image_url
        return None
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120))
    user_avatar = db.Column(db.String(50), default='👤')
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review for Product {self.product_id} by {self.user_name}>'


class AffiliateClick(db.Model):
    __tablename__ = 'affiliate_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(300))
    referrer = db.Column(db.String(500))
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AffiliateClick Product {self.product_id} at {self.clicked_at}>'


class UserProductView(db.Model):
    __tablename__ = 'user_product_views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_view'),)
    
    def __repr__(self):
        return f'<UserProductView User {self.user_id} Product {self.product_id}>'


class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSetting {self.key}={self.value}>'


# ==================== ORDER MODELS ====================

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'