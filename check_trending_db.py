# check_trending_db.py
from app import app, db
from models import Product

with app.app_context():
    print("=" * 50)
    print("ALL PRODUCTS IN DATABASE:")
    print("=" * 50)
    
    all_products = Product.query.all()
    for p in all_products:
        print(f"ID: {p.id} | Name: {p.name[:40]} | is_trending: {p.is_trending} | is_featured: {p.is_featured}")
    
    print("\n" + "=" * 50)
    trending = Product.query.filter_by(is_trending=True).all()
    print(f"TRENDING PRODUCTS COUNT: {len(trending)}")
    for p in trending:
        print(f"  ✅ {p.name}")