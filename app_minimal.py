from flask import Flask, render_template
from models import db, BlogPost
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///affiliate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables and test post when app starts
with app.app_context():
    db.create_all()
    
    # Check if post exists
    post = BlogPost.query.filter_by(slug='why-pastel-niches-convert').first()
    if not post:
        print("📝 Creating test post...")
        post = BlogPost(
            title="Why Pastel Niches Convert Better in 2026",
            slug="why-pastel-niches-convert",
            content="<p>This is a test blog post content. Learn how aesthetic affiliate marketing boosts trust and sales.</p><h2>Key Points</h2><ul><li>Point 1</li><li>Point 2</li><li>Point 3</li></ul>",
            excerpt="Learn how aesthetic affiliate marketing boosts trust and sales.",
            category="Strategy",
            author="Sarah Johnson",
            image_icon="fas fa-chart-line",
            views=0
        )
        db.session.add(post)
        db.session.commit()
        print("✅ Test post created!")
    else:
        print("✅ Test post already exists!")

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; }
            h1 { color: #1a1a1a; }
            a { color: #1a1a1a; text-decoration: none; border: 1px solid #333; padding: 10px 20px; border-radius: 40px; display: inline-block; margin: 10px 0; }
            a:hover { background: #333; color: white; }
        </style>
    </head>
    <body>
        <h1>Hello World!</h1>
        <p>Flask is working!</p>
        <p><a href="/blog/why-pastel-niches-convert">View Blog Post</a></p>
        <p><a href="/show-posts">Show All Posts</a></p>
        <p><a href="/routes">Show All Routes</a></p>
    </body>
    </html>
    """

@app.route('/blog/<slug>')
def blog_post(slug):
    try:
        post = BlogPost.query.filter_by(slug=slug).first()
        
        if not post:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Not Found</title></head>
            <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
                <h1>Post not found!</h1>
                <p>Slug: <code>{slug}</code></p>
                <p><a href="/show-posts">Show all posts</a></p>
                <p><a href="/">Go Home</a></p>
            </body>
            </html>
            """
        
        # Increment views
        post.views += 1
        db.session.commit()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{post.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.8; }}
                h1 {{ color: #1a1a1a; font-size: 2.5rem; }}
                .meta {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 15px; margin-bottom: 20px; }}
                .content {{ line-height: 1.8; }}
                .back {{ display: inline-block; padding: 10px 24px; border: 1px solid #333; border-radius: 40px; text-decoration: none; color: #333; margin-top: 30px; }}
                .back:hover {{ background: #333; color: white; }}
            </style>
        </head>
        <body>
            <h1>{post.title}</h1>
            <div class="meta">
                <strong>Author:</strong> {post.author} &bull; 
                <strong>Category:</strong> {post.category} &bull; 
                <strong>Views:</strong> {post.views}
            </div>
            <div class="content">
                {post.content}
            </div>
            <a href="/" class="back">← Back to Home</a>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.route('/show-posts')
def show_posts():
    posts = BlogPost.query.all()
    
    if not posts:
        return """
        <!DOCTYPE html>
        <html>
        <head><title>No Posts</title></head>
        <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
            <h1>No posts found!</h1>
            <p>The database is empty.</p>
            <p><a href="/">Go Home</a></p>
        </body>
        </html>
        """
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Posts</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; }
            h1 { color: #1a1a1a; }
            .post { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .post a { color: #1a1a1a; }
            .slug { color: #666; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <h1>All Posts in Database</h1>
    """
    
    for p in posts:
        html += f"""
        <div class="post">
            <strong>{p.title}</strong><br>
            <span class="slug">Slug: {p.slug}</span><br>
            Author: {p.author} | Category: {p.category} | Views: {p.views}<br>
            <a href="/blog/{p.slug}">View Post</a>
        </div>
        """
    
    html += """
        <p><a href="/">Go Home</a></p>
    </body>
    </html>
    """
    return html

@app.route('/routes')
def list_routes():
    """Show all registered routes"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Routes</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px; }
            li { padding: 5px 0; }
        </style>
    </head>
    <body>
        <h1>All Registered Routes</h1>
        <ul>
    """
    for rule in app.url_map.iter_rules():
        html += f"<li><code>{rule}</code></li>"
    html += """
        </ul>
        <p><a href="/">Go Home</a></p>
    </body>
    </html>
    """
    return html

@app.route('/create-test-post')
def create_test_post():
    try:
        post = BlogPost.query.filter_by(slug='why-pastel-niches-convert').first()
        if post:
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Already Exists</title></head>
            <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
                <h1>Post already exists!</h1>
                <p><a href="/blog/why-pastel-niches-convert">View Post</a></p>
                <p><a href="/">Go Home</a></p>
            </body>
            </html>
            """
        
        post = BlogPost(
            title="Why Pastel Niches Convert Better in 2026",
            slug="why-pastel-niches-convert",
            content="<p>This is a test blog post content. Learn how aesthetic affiliate marketing boosts trust and sales.</p><h2>Key Points</h2><ul><li>Point 1</li><li>Point 2</li><li>Point 3</li></ul>",
            excerpt="Learn how aesthetic affiliate marketing boosts trust and sales.",
            category="Strategy",
            author="Sarah Johnson",
            image_icon="fas fa-chart-line",
            views=0
        )
        db.session.add(post)
        db.session.commit()
        
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Created</title></head>
        <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
            <h1>✅ Test Post Created!</h1>
            <p><a href="/blog/why-pastel-niches-convert">View Post</a></p>
            <p><a href="/show-posts">Show all posts</a></p>
            <p><a href="/">Go Home</a></p>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Flask Server...")
    print("=" * 50)
    print("📝 Routes available:")
    print("   http://127.0.0.1:5000/")
    print("   http://127.0.0.1:5000/blog/why-pastel-niches-convert")
    print("   http://127.0.0.1:5000/show-posts")
    print("   http://127.0.0.1:5000/routes")
    print("   http://127.0.0.1:5000/create-test-post")
    print("=" * 50)
    app.run(debug=True, port=5000)