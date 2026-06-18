# force_set_trending.py
from app import app, db
from models import Product

with app.app_context():
    # Get first 6 products
    products = Product.query.limit(6).all()
    count = 0
    
    for product in products:
        product.is_trending = True
        count += 1
        print(f"✅ Set as trending: {product.name}")
    
    db.session.commit()
    print(f"\n📊 Total {count} products marked as trending!")
    
    # Verify
    trending = Product.query.filter_by(is_trending=True).all()
    print(f"\nNow {len(trending)} products are trending:")
    for p in trending:
        print(f"  - {p.name}")