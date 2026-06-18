# fix_database.py
import sqlite3

def fix_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/affiliate.db')
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print("Current columns:", columns)
        
        # Add image_url column if it doesn't exist
        if 'image_url' not in columns:
            print("Adding image_url column...")
            cursor.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)")
            print("✅ image_url column added")
        else:
            print("image_url column already exists")
        
        # Add image_file column if it doesn't exist
        if 'image_file' not in columns:
            print("Adding image_file column...")
            cursor.execute("ALTER TABLE products ADD COLUMN image_file VARCHAR(200)")
            print("✅ image_file column added")
        else:
            print("image_file column already exists")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database fixed successfully!")
        print("You can now restart your Flask servers.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()