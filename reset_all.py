# reset_all.py
import os
import shutil

print("=" * 50)
print("🔧 RESETTING DATABASE...")
print("=" * 50)

# Delete all database files
db_files = ['affiliate.db', 'site.db', 'instance/affiliate.db', 'instance/site.db']
for db_file in db_files:
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Deleted: {db_file}")

# Delete migrations folder if exists
if os.path.exists('migrations'):
    shutil.rmtree('migrations')
    print("✅ Deleted: migrations folder")

print("=" * 50)
print("✅ Database reset complete!")
print("Now run: python admin_app.py")
print("=" * 50)