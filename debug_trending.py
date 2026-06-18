# debug_trending.py
from app import app, db
from models import Product

with app.app_context():
    print("\n" + "=" * 60)
    print("DATABASE CHECK")
    print("=" * 60)
    
    # Count total products
    total = Product.query.count()
    print(f"Total products in database: {total}")
    
    # Check trending products
    trending = Product.query.filter_by(is_trending=True).all()
    print(f"Trending products found: {len(trending)}")
    
    if len(trending) == 0:
        print("\n⚠️ NO TRENDING PRODUCTS FOUND!")
        print("\nLet's fix this by setting some products as trending...")
        
        # Set first 6 products as trending
        products = Product.query.limit(6).all()
        count = 0
        for p in products:
            p.is_trending = True
            count += 1
            print(f"  ✅ Set as trending: {p.name}")
        
        db.session.commit()
        print(f"\n✅ {count} products marked as trending!")
        
        # Verify again
        trending = Product.query.filter_by(is_trending=True).all()
        print(f"\nNow trending products: {len(trending)}")
        for p in trending:
            print(f"  🔥 {p.name}")
    else:
        print("\n✅ Trending products found:")
        for p in trending:
            print(f"  🔥 {p.name}")
    
    print("=" * 60)