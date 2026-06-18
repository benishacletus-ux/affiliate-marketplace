# bulk_add_products.py - Fast bulk insert
from app import app, db
from models import Category, Product
import random
from datetime import datetime
import time

def bulk_add_products(total=10000):
    """Ultra-fast bulk insert using SQLAlchemy core"""
    
    start_time = time.time()
    
    categories = Category.query.all()
    cat_ids = [c.id for c in categories]
    
    if not cat_ids:
        print("No categories found!")
        return
    
    # Pre-generate all products in memory
    products = []
    
    names = [
        'Premium', 'Ultra', 'Pro', 'Max', 'Elite', 'Essential', 'Deluxe', 'Standard',
        'Wireless', 'Smart', 'Digital', 'Portable', 'Compact', 'Heavy Duty', 'Lightweight'
    ]
    
    items = [
        'Headphones', 'Speaker', 'Watch', 'Phone', 'Tablet', 'Laptop', 'Camera', 'Drone',
        'Keyboard', 'Mouse', 'Monitor', 'Chair', 'Desk', 'Lamp', 'Pillow', 'Blanket',
        'Mat', 'Bottle', 'Bag', 'Shoes', 'Shirt', 'Jacket', 'Glasses', 'Watch'
    ]
    
    print(f"Generating {total} products...")
    
    for i in range(1, total + 1):
        category_id = random.choice(cat_ids)
        name = f"{random.choice(names)} {random.choice(items)} {i}"
        slug = f"product-{i}-{random.randint(1000, 9999)}"
        price = round(random.uniform(19.99, 499.99), 2)
        
        product = Product(
            name=name[:100],
            slug=slug[:100],
            description=f"High-quality {name.lower()} - perfect for everyday use. Great value!",
            price=price,
            original_price=round(price * random.uniform(1.2, 1.8), 2) if random.random() > 0.3 else None,
            affiliate_link=f"https://amzn.to/aff-{i}",
            image_icon=random.choice(['fas fa-tag', 'fas fa-box', 'fas fa-gem', 'fas fa-star']),
            rating=round(random.uniform(3.8, 4.9), 1),
            reviews_count=random.randint(0, 5000),
            category_id=category_id,
            is_trending=random.random() > 0.95,
            is_featured=random.random() > 0.9,
            commission_rate=random.choice([5, 8, 10, 12, 15, 20]),
            click_count=0,
            created_at=datetime.utcnow()
        )
        products.append(product)
        
        if i % 1000 == 0:
            print(f"Generated {i} products...")
    
    print("Inserting into database...")
    
    # Bulk insert
    db.session.bulk_save_objects(products)
    db.session.commit()
    
    elapsed = time.time() - start_time
    print(f"\n✅ Added {total} products in {elapsed:.2f} seconds!")
    print(f"Total products: {Product.query.count()}")

if __name__ == '__main__':
    with app.app_context():
        try:
            num = int(input("Number of products to add (5000, 10000, 50000): ") or 10000)
            bulk_add_products(num)
        except KeyboardInterrupt:
            print("\nCancelled")
        except Exception as e:
            print(f"Error: {e}")