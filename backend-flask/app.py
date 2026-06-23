from flask import Flask, jsonify, request, session, render_template_string, send_from_directory
from flask_cors import CORS
from functools import wraps
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Profile, SocialLink, UserSocialLink, AboutSection, Timeline, Skill, Project, BlogPost, ContactMessage
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)

# Initialize extensions
db.init_app(app)
CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to normalize image URLs for production
def normalize_image_url(url):
    """Convert localhost URLs to relative paths or production URLs"""
    if not url:
        return None
    
    # If URL is already a relative path starting with /, return as is
    if url.startswith('/'):
        return url
    
    # If URL contains localhost:5000 or 127.0.0.1:5000, extract the path
    if 'localhost:5000' in url or '127.0.0.1:5000' in url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Return the path part (e.g., /static/uploads/profiles/image.jpg)
            return parsed.path if parsed.path else url
        except:
            # Fallback: try to extract path manually
            if '/static/' in url:
                return '/static/' + url.split('/static/')[1]
            return url
    
    # If URL is already a full URL (http/https), return as is (external URLs)
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Default: assume it's a filename and make it a relative path
    # This handles cases where just filename is stored (e.g., "image.jpg")
    return f'/{url}' if not url.startswith('/') else url

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROOT ROUTE ====================

@app.route('/', methods=['GET'])
def index():
    """API root endpoint with available routes"""
    return jsonify({
        'message': 'Personal Portfolio API',
        'version': '1.0.0',
        'endpoints': {
            'profile': '/api/profile',
            'timeline': '/api/timeline',
            'skills': '/api/skills',
            'projects': '/api/projects',
            'blog': '/api/blog',
            'contact': '/api/contact',
            'health': '/api/health'
        },
        'documentation': 'See README.md for API documentation'
    })

# ==================== PROFILE ROUTES ====================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get profile information"""
    profile = Profile.query.first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    social_links = SocialLink.query.filter_by(profile_id=profile.id).order_by(SocialLink.display_order).all()
    
    return jsonify({
        'id': profile.id,
        'name': profile.name,
        'title': profile.title,
        'description': profile.description,
        'profile_image_url': normalize_image_url(profile.profile_image_url),
        'email': profile.email,
        'phone': profile.phone,
        'location': profile.location,
        'social_links': [{
            'id': link.id,
            'platform': link.platform,
            'url': link.url,
            'icon_name': link.icon_name,
            'display_order': link.display_order
        } for link in social_links]
    })

@app.route('/api/profile', methods=['POST', 'PUT'])
def update_profile():
    """Create or update profile"""
    data = request.get_json()
    
    profile = Profile.query.first()
    if not profile:
        profile = Profile()
    
    profile.name = data.get('name', profile.name)
    profile.title = data.get('title', profile.title)
    profile.description = data.get('description', profile.description)
    profile.profile_image_url = data.get('profile_image_url', profile.profile_image_url)
    profile.email = data.get('email', profile.email)
    profile.phone = data.get('phone', profile.phone)
    profile.location = data.get('location', profile.location)
    profile.updated_at = datetime.utcnow()
    
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully', 'id': profile.id}), 200

# ==================== ABOUT SECTION ROUTES ====================

@app.route('/api/about', methods=['GET'])
def get_about_section():
    """Get about section configuration"""
    config = AboutSection.query.first()
    if not config:
        # Create default if doesn't exist
        config = AboutSection(
            title="My Journey",
            subtitle="From code to cloud - a timeline of growth and innovation",
            skills_title="Core Competencies"
        )
        db.session.add(config)
        db.session.commit()
    return jsonify({
        'id': config.id,
        'title': config.title,
        'subtitle': config.subtitle,
        'skills_title': config.skills_title
    })

@app.route('/api/about', methods=['PUT'])
@login_required
def update_about_section():
    """Update about section configuration"""
    config = AboutSection.query.first()
    if not config:
        config = AboutSection(
            title="My Journey",
            subtitle="From code to cloud - a timeline of growth and innovation",
            skills_title="Core Competencies"
        )
        db.session.add(config)
    
    data = request.get_json()
    config.title = data.get('title', config.title)
    config.subtitle = data.get('subtitle', config.subtitle)
    config.skills_title = data.get('skills_title', config.skills_title)
    config.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'About section updated'}), 200

# ==================== TIMELINE ROUTES ====================

@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """Get all timeline entries"""
    timeline = Timeline.query.order_by(Timeline.display_order, Timeline.year.desc()).all()
    
    return jsonify([{
        'id': item.id,
        'year': item.year,
        'title': item.title,
        'company': item.company,
        'description': item.description,
        'icon_name': item.icon_name,
        'skills': item.skills.split(',') if item.skills else [],
        'display_order': item.display_order
    } for item in timeline])

@app.route('/api/timeline', methods=['POST'])
@login_required
def create_timeline():
    """Create a new timeline entry"""
    data = request.get_json()
    
    timeline = Timeline(
        year=data.get('year'),
        title=data.get('title'),
        company=data.get('company'),
        description=data.get('description'),
        icon_name=data.get('icon_name'),
        skills=','.join(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills'),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(timeline)
    db.session.commit()
    
    return jsonify({'message': 'Timeline entry created', 'id': timeline.id}), 201

@app.route('/api/timeline/<int:id>', methods=['PUT'])
@login_required
def update_timeline(id):
    """Update a timeline entry"""
    timeline = Timeline.query.get_or_404(id)
    data = request.get_json()
    
    timeline.year = data.get('year', timeline.year)
    timeline.title = data.get('title', timeline.title)
    timeline.company = data.get('company', timeline.company)
    timeline.description = data.get('description', timeline.description)
    timeline.icon_name = data.get('icon_name', timeline.icon_name)
    timeline.skills = ','.join(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills', timeline.skills)
    timeline.display_order = data.get('display_order', timeline.display_order)
    timeline.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Timeline entry updated'}), 200

@app.route('/api/timeline/<int:id>', methods=['GET'])
def get_timeline_entry(id):
    """Get a single timeline entry"""
    timeline = Timeline.query.get_or_404(id)
    
    return jsonify({
        'id': timeline.id,
        'year': timeline.year,
        'title': timeline.title,
        'company': timeline.company,
        'description': timeline.description,
        'icon_name': timeline.icon_name,
        'skills': timeline.skills.split(',') if timeline.skills else [],
        'display_order': timeline.display_order
    })

@app.route('/api/timeline/<int:id>', methods=['DELETE'])
@login_required
def delete_timeline(id):
    """Delete a timeline entry"""
    timeline = Timeline.query.get_or_404(id)
    db.session.delete(timeline)
    db.session.commit()
    
    return jsonify({'message': 'Timeline entry deleted'}), 200

# ==================== SKILLS ROUTES ====================

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get all skills"""
    skills = Skill.query.order_by(Skill.display_order).all()
    
    return jsonify([{
        'id': skill.id,
        'name': skill.name,
        'level': skill.level,
        'color': skill.color,
        'display_order': skill.display_order
    } for skill in skills])

@app.route('/api/skills', methods=['POST'])
@login_required
def create_skill():
    """Create a new skill"""
    data = request.get_json()
    
    skill = Skill(
        name=data.get('name'),
        level=data.get('level', 0),
        color=data.get('color'),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(skill)
    db.session.commit()
    
    return jsonify({'message': 'Skill created', 'id': skill.id}), 201

@app.route('/api/skills/<int:id>', methods=['GET'])
def get_skill(id):
    """Get a single skill"""
    skill = Skill.query.get_or_404(id)
    
    return jsonify({
        'id': skill.id,
        'name': skill.name,
        'level': skill.level,
        'color': skill.color,
        'display_order': skill.display_order
    })

@app.route('/api/skills/<int:id>', methods=['PUT'])
@login_required
def update_skill(id):
    """Update a skill"""
    skill = Skill.query.get_or_404(id)
    data = request.get_json()
    
    skill.name = data.get('name', skill.name)
    skill.level = data.get('level', skill.level)
    skill.color = data.get('color', skill.color)
    skill.display_order = data.get('display_order', skill.display_order)
    skill.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Skill updated'}), 200

@app.route('/api/skills/<int:id>', methods=['DELETE'])
@login_required
def delete_skill(id):
    """Delete a skill"""
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    return jsonify({'message': 'Skill deleted'}), 200

# ==================== PROJECTS ROUTES ====================

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    # Only return projects with status=True for public API
    status_filter = request.args.get('status', None)
    query = Project.query
    
    if status_filter is None:
        # Default: only show active projects for public
        # Filter by status=True, excluding NULL values
        query = query.filter(Project.status == True)
    elif status_filter.lower() == 'all':
        # Admin panel can request all projects
        pass
    else:
        # Filter by status if specified
        query = query.filter_by(status=(status_filter.lower() == 'true'))
    
    projects = query.order_by(Project.display_order, Project.created_at.desc()).all()
    
    return jsonify([{
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'image_url': normalize_image_url(project.image_url),
        'tags': project.tags.split(',') if project.tags else [],
        'icon_name': project.icon_name,
        'gradient': project.gradient,
        'github_url': project.github_url,
        'demo_url': project.demo_url,
        'is_featured': project.is_featured,
        'status': project.status,
        'display_order': project.display_order
    } for project in projects])

@app.route('/api/projects/<int:id>', methods=['GET'])
def get_project(id):
    """Get a single project"""
    project = Project.query.get_or_404(id)
    
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'image_url': normalize_image_url(project.image_url),
        'tags': project.tags.split(',') if project.tags else [],
        'icon_name': project.icon_name,
        'gradient': project.gradient,
        'github_url': project.github_url,
        'demo_url': project.demo_url,
        'is_featured': project.is_featured,
        'status': project.status,
        'display_order': project.display_order
    })

@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Create a new project"""
    data = request.get_json()
    
    project = Project(
        title=data.get('title'),
        description=data.get('description'),
        image_url=data.get('image_url'),
        tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags'),
        icon_name=data.get('icon_name'),
        gradient=data.get('gradient'),
        github_url=data.get('github_url'),
        demo_url=data.get('demo_url'),
        is_featured=data.get('is_featured', False),
        status=data.get('status', True),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({'message': 'Project created', 'id': project.id}), 201

@app.route('/api/projects/<int:id>', methods=['PUT'])
@login_required
def update_project(id):
    """Update a project"""
    project = Project.query.get_or_404(id)
    data = request.get_json()
    
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.image_url = data.get('image_url', project.image_url)
    project.tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', project.tags)
    project.icon_name = data.get('icon_name', project.icon_name)
    project.gradient = data.get('gradient', project.gradient)
    project.github_url = data.get('github_url', project.github_url)
    project.demo_url = data.get('demo_url', project.demo_url)
    project.is_featured = data.get('is_featured', project.is_featured)
    project.status = data.get('status', project.status) if 'status' in data else project.status
    project.display_order = data.get('display_order', project.display_order)
    project.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Project updated'}), 200

@app.route('/api/projects/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    """Delete a project"""
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200

# ==================== BLOG ROUTES ====================

@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    """Get all blog posts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    featured_only = request.args.get('featured', False, type=bool)
    all_posts = request.args.get('all', False, type=bool)  # Admin panel için tüm yazılar
    
    # Limit per_page to prevent excessive queries
    max_per_page = 100
    if per_page > max_per_page:
        per_page = max_per_page
    
    # Admin panelinde tüm yazıları göster, normal kullanıcılar için sadece yayınlanmışları
    query = BlogPost.query
    if not all_posts:
        # Filter by is_published=True, excluding NULL values
        query = query.filter(BlogPost.is_published == True)
    if featured_only:
        query = query.filter_by(is_featured=True)
    
    try:
        pagination = query.order_by(BlogPost.display_order, BlogPost.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    except Exception as e:
        app.logger.error(f"Pagination error: {str(e)}")
        return jsonify({'error': 'Failed to fetch blog posts', 'details': str(e)}), 500
    
    return jsonify({
        'posts': [{
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'content': post.content,
            'image_url': normalize_image_url(post.image_url),
            'url': post.url,
            'category': post.category,
            'date': post.date.isoformat() if post.date else None,
            'read_time': post.read_time,
            'author': post.author,
            'is_featured': post.is_featured,
            'is_published': post.is_published
        } for post in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/api/blog/<int:id>', methods=['GET'])
def get_blog_post(id):
    """Get a single blog post"""
    post = BlogPost.query.get_or_404(id)
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'excerpt': post.excerpt,
        'content': post.content,
        'image_url': normalize_image_url(post.image_url),
        'url': post.url,
        'category': post.category,
        'date': post.date.isoformat() if post.date else None,
        'read_time': post.read_time,
        'author': post.author,
        'is_featured': post.is_featured,
        'is_published': post.is_published
    })

@app.route('/api/blog', methods=['POST'])
@login_required
def create_blog_post():
    """Create a new blog post"""
    data = request.get_json()
    
    post = BlogPost(
        title=data.get('title'),
        excerpt=data.get('excerpt'),
        content=data.get('content'),
        image_url=data.get('image_url'),
        url=data.get('url'),
        category=data.get('category'),
        date=datetime.fromisoformat(data.get('date')) if data.get('date') else datetime.utcnow(),
        read_time=data.get('read_time'),
        author=data.get('author'),
        is_featured=data.get('is_featured', False),
        is_published=data.get('is_published', True),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'message': 'Blog post created', 'id': post.id}), 201

@app.route('/api/blog/<int:id>', methods=['PUT'])
@login_required
def update_blog_post(id):
    """Update a blog post"""
    post = BlogPost.query.get_or_404(id)
    data = request.get_json()
    
    post.title = data.get('title', post.title)
    post.excerpt = data.get('excerpt', post.excerpt)
    post.content = data.get('content', post.content)
    post.image_url = data.get('image_url', post.image_url)
    post.url = data.get('url', post.url)
    post.category = data.get('category', post.category)
    if data.get('date'):
        post.date = datetime.fromisoformat(data.get('date'))
    post.read_time = data.get('read_time', post.read_time)
    post.author = data.get('author', post.author)
    post.is_featured = data.get('is_featured', post.is_featured)
    post.is_published = data.get('is_published', post.is_published)
    post.display_order = data.get('display_order', post.display_order)
    post.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Blog post updated'}), 200

@app.route('/api/blog/<int:id>', methods=['DELETE'])
@login_required
def delete_blog_post(id):
    """Delete a blog post"""
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted'}), 200

# ==================== CONTACT ROUTES ====================

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    data = request.get_json()
    
    message = ContactMessage(
        name=data.get('name'),
        email=data.get('email'),
        subject=data.get('subject'),
        message=data.get('message')
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'message': 'Contact message submitted successfully', 'id': message.id}), 201

@app.route('/api/contact/messages', methods=['GET'])
@login_required
def get_contact_messages():
    """Get all contact messages (admin)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'messages': [{
            'id': msg.id,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message,
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat() if msg.created_at else None
        } for msg in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session.permanent = True
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name
                }
            }), 200
    return jsonify({'authenticated': False}), 200

# ==================== ADMIN ROUTES ====================

@app.route('/admin', methods=['GET'])
def admin_panel():
    """Admin panel HTML page"""
    admin_html = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel - Personal Portfolio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 { font-size: 2em; margin-bottom: 10px; }
            .login-form {
                padding: 40px;
                max-width: 400px;
                margin: 0 auto;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover { transform: translateY(-2px); }
            button:disabled { opacity: 0.6; cursor: not-allowed; }
            .error {
                background: #fee;
                color: #c33;
                padding: 12px;
                border-radius: 5px;
                margin-bottom: 20px;
                display: none;
            }
            .dashboard {
                display: none;
                padding: 30px;
            }
            .dashboard-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e0e0e0;
            }
            .logout-btn {
                width: auto;
                padding: 10px 20px;
                background: #dc3545;
            }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #e0e0e0;
            }
            .tab {
                padding: 12px 24px;
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
                color: #666;
                border-bottom: 3px solid transparent;
                transition: all 0.3s;
            }
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-card h3 {
                font-size: 2em;
                margin-bottom: 5px;
            }
            .stat-card p {
                opacity: 0.9;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
                table-layout: fixed;
            }
            th, td {
                padding: 16px;
                text-align: left;
                border-bottom: 1px solid #e8e8e8;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 600;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            table.messages-table th:nth-child(1),
            table.messages-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.messages-table th:nth-child(2),
            table.messages-table td:nth-child(2) {
                width: 150px;
            }
            table.messages-table th:nth-child(3),
            table.messages-table td:nth-child(3) {
                width: 200px;
            }
            table.messages-table th:nth-child(4),
            table.messages-table td:nth-child(4) {
                width: 200px;
            }
            table.messages-table th:nth-child(5),
            table.messages-table td:nth-child(5) {
                width: auto;
                min-width: 250px;
            }
            table.messages-table th:nth-child(6),
            table.messages-table td:nth-child(6) {
                width: 150px;
            }
            /* Social Links Table */
            table.social-links-table th:nth-child(1),
            table.social-links-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.social-links-table th:nth-child(2),
            table.social-links-table td:nth-child(2) {
                width: 150px;
            }
            table.social-links-table th:nth-child(3),
            table.social-links-table td:nth-child(3) {
                width: auto;
                min-width: 250px;
            }
            table.social-links-table th:nth-child(4),
            table.social-links-table td:nth-child(4) {
                width: 150px;
            }
            table.social-links-table th:nth-child(5),
            table.social-links-table td:nth-child(5) {
                width: 200px;
                text-align: center;
            }
            /* Timeline Table */
            table.timeline-table th:nth-child(1),
            table.timeline-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.timeline-table th:nth-child(2),
            table.timeline-table td:nth-child(2) {
                width: 100px;
                text-align: center;
            }
            table.timeline-table th:nth-child(3),
            table.timeline-table td:nth-child(3) {
                width: auto;
                min-width: 200px;
            }
            table.timeline-table th:nth-child(4),
            table.timeline-table td:nth-child(4) {
                width: auto;
                min-width: 200px;
            }
            table.timeline-table th:nth-child(5),
            table.timeline-table td:nth-child(5) {
                width: 200px;
                text-align: center;
            }
            /* Skills Table */
            table.skills-table th:nth-child(1),
            table.skills-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.skills-table th:nth-child(2),
            table.skills-table td:nth-child(2) {
                width: auto;
                min-width: 200px;
            }
            table.skills-table th:nth-child(3),
            table.skills-table td:nth-child(3) {
                width: 120px;
                text-align: center;
            }
            table.skills-table th:nth-child(4),
            table.skills-table td:nth-child(4) {
                width: 120px;
                text-align: center;
            }
            table.skills-table th:nth-child(5),
            table.skills-table td:nth-child(5) {
                width: 200px;
                text-align: center;
            }
            /* Projects Table */
            table.projects-table th:nth-child(1),
            table.projects-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.projects-table th:nth-child(2),
            table.projects-table td:nth-child(2) {
                width: auto;
                min-width: 200px;
            }
            table.projects-table th:nth-child(3),
            table.projects-table td:nth-child(3) {
                width: auto;
                min-width: 300px;
            }
            table.projects-table th:nth-child(4),
            table.projects-table td:nth-child(4) {
                width: 200px;
                text-align: center;
            }
            /* Blog Table */
            table.blog-table th:nth-child(1),
            table.blog-table td:nth-child(1) {
                width: 60px;
                text-align: center;
            }
            table.blog-table th:nth-child(2),
            table.blog-table td:nth-child(2) {
                width: auto;
                min-width: 250px;
            }
            table.blog-table th:nth-child(3),
            table.blog-table td:nth-child(3) {
                width: 150px;
            }
            table.blog-table th:nth-child(4),
            table.blog-table td:nth-child(4) {
                width: 150px;
                text-align: center;
            }
            table.blog-table th:nth-child(5),
            table.blog-table td:nth-child(5) {
                width: 200px;
                text-align: center;
            }
            tr:hover {
                background: #f8f9fa;
            }
            tr:last-child td {
                border-bottom: none;
            }
            .message-preview {
                max-width: 300px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                cursor: pointer;
                color: #667eea;
                text-decoration: underline;
            }
            .message-preview:hover {
                color: #764ba2;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                overflow: auto;
            }
            .modal-content {
                background: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 10px;
                width: 80%;
                max-width: 700px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #e0e0e0;
            }
            .modal-header h3 {
                margin: 0;
                color: #333;
            }
            .close {
                color: #aaa;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                line-height: 20px;
            }
            .close:hover {
                color: #000;
            }
            .modal-body {
                line-height: 1.6;
            }
            .modal-field {
                margin-bottom: 20px;
            }
            .modal-field label {
                font-weight: 600;
                color: #667eea;
                display: block;
                margin-bottom: 5px;
            }
            .modal-field p {
                color: #555;
                margin: 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                word-wrap: break-word;
            }
            .form-section {
                background: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            /* Accordion row styles */
            .accordion-row {
                display: none;
                background: #f8f9fa;
            }
            .accordion-row.active {
                display: table-row;
            }
            .accordion-row td {
                padding: 0;
                border-bottom: 1px solid #e8e8e8;
            }
            .accordion-content {
                padding: 20px;
                background: #f8f9fa;
                overflow: hidden;
                transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
            }
            .accordion-row.active .accordion-content {
                max-height: 2000px;
                opacity: 1;
            }
            .accordion-row:not(.active) .accordion-content {
                max-height: 0;
                opacity: 0;
                padding: 0 20px;
            }
            .accordion-form {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
            }
            .success {
                background: #d4edda;
                color: #155724;
                padding: 12px;
                border-radius: 5px;
                margin-bottom: 20px;
                display: none;
            }
            .btn-danger {
                background: #dc3545;
                color: white;
                padding: 8px 10px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-left: 5px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
            }
            .btn-danger:hover {
                background: #c82333;
            }
            .btn-edit {
                background: #28a745;
                color: white;
                padding: 8px 10px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
            }
            .btn-edit:hover {
                background: #218838;
            }
            .btn-icon {
                width: 18px;
                height: 18px;
                fill: currentColor;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Admin Panel</h1>
                <p>Personal Portfolio Yönetim Paneli</p>
            </div>
            
            <div id="loginForm" class="login-form">
                <div class="error" id="errorMsg"></div>
                <div class="form-group">
                    <label>Kullanıcı Adı</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label>Şifre</label>
                    <input type="password" id="password" required>
                </div>
                <button onclick="login()">Giriş Yap</button>
            </div>
            
            <div id="dashboard" class="dashboard">
                <div class="dashboard-header">
                    <h2>Hoş Geldiniz, <span id="userName"></span></h2>
                    <button class="logout-btn" onclick="logout()">Çıkış Yap</button>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="showTab('overview', event)">Genel Bakış</button>
                    <button class="tab" onclick="showTab('profile', event)">Profil</button>
                    <button class="tab" onclick="showTab('timeline', event)">Timeline</button>
                    <button class="tab" onclick="showTab('skills', event)">Yetenekler</button>
                    <button class="tab" onclick="showTab('projects', event)">Projeler</button>
                    <button class="tab" onclick="showTab('blog', event)">Blog</button>
                    <button class="tab" onclick="showTab('messages', event)">Mesajlar</button>
                </div>
                
                <div id="overview" class="tab-content active">
                    <div class="stats">
                        <div class="stat-card">
                            <h3 id="projectsCount">0</h3>
                            <p>Proje</p>
                        </div>
                        <div class="stat-card">
                            <h3 id="blogCount">0</h3>
                            <p>Blog Yazısı</p>
                        </div>
                        <div class="stat-card">
                            <h3 id="messagesCount">0</h3>
                            <p>Mesaj</p>
                        </div>
                    </div>
                </div>
                
                <div id="profile" class="tab-content">
                    <div class="form-section">
                        <h3>Kişisel Bilgiler</h3>
                        <div class="form-group">
                            <label>Ad Soyad</label>
                            <input type="text" id="fullName">
                        </div>
                        <div class="form-group">
                            <label>E-posta</label>
                            <input type="email" id="userEmail">
                        </div>
                        <div class="form-group">
                            <label>Telefon</label>
                            <input type="text" id="userPhone">
                        </div>
                        <div class="form-group">
                            <label>Konum</label>
                            <input type="text" id="userLocation">
                        </div>
                        <div class="form-group">
                            <label>Meslek Unvanı (Title)</label>
                            <input type="text" id="profileTitle" placeholder="Full-Stack & DevOps Engineer">
                            <small style="color: #666; display: block; margin-top: 5px;">Hero section&#39;da ismin altında gösterilecek unvan</small>
                        </div>
                        <div class="form-group">
                            <label>Biyografi</label>
                            <textarea id="userBio" rows="4"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Profil Resmi</label>
                            <div style="margin-bottom: 10px;">
                                <input type="file" id="userProfileImage" accept="image/png,image/jpeg,image/jpg,image/gif,image/webp" style="margin-bottom: 10px;" />
                                <button onclick="uploadProfileImage()" style="width: auto; padding: 8px 16px; font-size: 14px; margin-left: 10px;">Yükle</button>
                                <button onclick="deleteProfileImage()" style="width: auto; padding: 8px 16px; font-size: 14px; margin-left: 10px; background: #dc3545;">Sil</button>
                            </div>
                            <div id="profileImagePreview" style="margin-top: 10px;">
                                <img id="currentProfileImage" src="" alt="Profil Resmi" style="max-width: 200px; max-height: 200px; border-radius: 8px; display: none; border: 2px solid #e0e0e0;">
                            </div>
                            <small style="color: #666; display: block; margin-top: 5px;">Hero section&#39;da gösterilecek profil resmi (PNG, JPG, JPEG, GIF, WEBP - Max 16MB)</small>
                        </div>
                        <button onclick="updateUserInfo()">Güncelle</button>
                    </div>
                    <div class="form-section">
                        <h3>About Section (My Journey) Başlıkları</h3>
                        <div class="form-group">
                            <label>Ana Başlık (Title)</label>
                            <input type="text" id="aboutTitle" placeholder="My Journey">
                        </div>
                        <div class="form-group">
                            <label>Alt Başlık (Subtitle)</label>
                            <input type="text" id="aboutSubtitle" placeholder="From code to cloud - a timeline of growth and innovation">
                        </div>
                        <div class="form-group">
                            <label>Yetenekler Başlığı (Skills Title)</label>
                            <input type="text" id="aboutSkillsTitle" placeholder="Core Competencies">
                        </div>
                        <button onclick="updateAboutSection()">Güncelle</button>
                    </div>
                    <div class="form-section">
                        <h3>Sosyal Medya Linkleri</h3>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <p style="margin: 0; color: #94a3b8;">"Connect With Me" alanında gösterilecek linkler</p>
                            <button onclick="showSocialLinkForm()" style="width: auto; padding: 8px 16px; font-size: 14px;">+ Yeni Link Ekle</button>
                        </div>
                        <div id="socialLinkForm" class="form-section" style="display: none; margin-bottom: 20px; background: #1e293b; padding: 20px; border-radius: 8px;">
                            <h4 id="socialLinkFormTitle">Yeni Sosyal Medya Linki Ekle</h4>
                            <div class="form-group">
                                <label>Platform *</label>
                                <input type="text" id="socialLinkPlatform" placeholder="GitHub, LinkedIn, Twitter, etc." required>
                            </div>
                            <div class="form-group">
                                <label>URL *</label>
                                <input type="text" id="socialLinkUrl" placeholder="https://github.com/username" required>
                            </div>
                            <div class="form-group">
                                <label>Icon Adı (Lucide Icons)</label>
                                <input type="text" id="socialLinkIconName" placeholder="Github, Linkedin, Twitter">
                            </div>
                            <div class="form-group">
                                <label>Sıralama</label>
                                <input type="number" id="socialLinkDisplayOrder" value="0">
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button onclick="saveSocialLink()">Kaydet</button>
                                <button onclick="cancelSocialLinkForm()" style="background: #6c757d;">İptal</button>
                            </div>
                        </div>
                        <div id="socialLinksList"></div>
                    </div>
                    <div class="form-section">
                        <h3>Şifre Değiştir</h3>
                        <div class="form-group">
                            <label>Yeni Şifre</label>
                            <input type="password" id="newPassword">
                        </div>
                        <div class="form-group">
                            <label>Şifre Tekrar</label>
                            <input type="password" id="confirmPassword">
                        </div>
                        <button onclick="changePassword()">Şifreyi Değiştir</button>
                    </div>
                </div>
                
                <div id="timeline" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Timeline (İş Deneyimleri)</h3>
                        <button onclick="showTimelineForm()" style="width: auto; padding: 10px 20px;">+ Yeni Timeline Ekle</button>
                    </div>
                    <div id="timelineForm" class="form-section" style="display: none; margin-bottom: 20px;">
                        <h4 id="timelineFormTitle">Yeni Timeline Ekle</h4>
                        <div class="form-group">
                            <label>Yıl *</label>
                            <input type="text" id="timelineYear" placeholder="2018" required>
                        </div>
                        <div class="form-group">
                            <label>Başlık (Pozisyon) *</label>
                            <input type="text" id="timelineTitle" placeholder="Frontend Developer" required>
                        </div>
                        <div class="form-group">
                            <label>Şirket *</label>
                            <input type="text" id="timelineCompany" placeholder="StartupCo" required>
                        </div>
                        <div class="form-group">
                            <label>Açıklama</label>
                            <textarea id="timelineDescription" rows="3" placeholder="Built responsive web applications..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Icon Adı</label>
                            <input type="text" id="timelineIconName" placeholder="Code2, Server, Cloud, Rocket">
                        </div>
                        <div class="form-group">
                            <label>Yetenekler (virgülle ayırın)</label>
                            <input type="text" id="timelineSkills" placeholder="React, TypeScript, Tailwind CSS">
                        </div>
                        <div class="form-group">
                            <label>Sıralama</label>
                            <input type="number" id="timelineDisplayOrder" value="0">
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="saveTimeline()">Kaydet</button>
                            <button onclick="cancelTimelineForm()" style="background: #6c757d;">İptal</button>
                        </div>
                    </div>
                    <div id="timelineList"></div>
                </div>
                
                <div id="skills" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Yetenekler (Skills)</h3>
                        <button onclick="showSkillForm()" style="width: auto; padding: 10px 20px;">+ Yeni Yetenek Ekle</button>
                    </div>
                    <div id="skillForm" class="form-section" style="display: none; margin-bottom: 20px;">
                        <h4 id="skillFormTitle">Yeni Yetenek Ekle</h4>
                        <div class="form-group">
                            <label>Yetenek Adı *</label>
                            <input type="text" id="skillName" placeholder="React & Next.js" required>
                        </div>
                        <div class="form-group">
                            <label>Seviye (0-100) *</label>
                            <input type="number" id="skillLevel" min="0" max="100" value="0" required>
                        </div>
                        <div class="form-group">
                            <label>Renk</label>
                            <select id="skillColor">
                                <option value="cyan">Cyan</option>
                                <option value="purple">Purple</option>
                                <option value="pink">Pink</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Sıralama</label>
                            <input type="number" id="skillDisplayOrder" value="0">
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="saveSkill()">Kaydet</button>
                            <button onclick="cancelSkillForm()" style="background: #6c757d;">İptal</button>
                        </div>
                    </div>
                    <div id="skillsList"></div>
                </div>
                
                <div id="projects" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Projeler</h3>
                        <button onclick="showProjectForm()" style="width: auto; padding: 10px 20px;">+ Yeni Proje Ekle</button>
                    </div>
                    <div id="projectForm" class="form-section" style="display: none; margin-bottom: 20px;">
                        <h4 id="projectFormTitle">Yeni Proje Ekle</h4>
                        <div class="form-group">
                            <label>Başlık *</label>
                            <input type="text" id="projectTitle" required>
                        </div>
                        <div class="form-group">
                            <label>Açıklama *</label>
                            <textarea id="projectDescription" rows="3" required></textarea>
                        </div>
                        <div class="form-group">
                            <label>Görsel URL</label>
                            <input type="text" id="projectImageUrl">
                        </div>
                        <div class="form-group">
                            <label>Etiketler (virgülle ayırın)</label>
                            <input type="text" id="projectTags" placeholder="React, Node.js, MongoDB">
                        </div>
                        <div class="form-group">
                            <label>Icon Adı</label>
                            <input type="text" id="projectIconName" placeholder="Cloud, Database, etc.">
                        </div>
                        <div class="form-group">
                            <label>Gradient</label>
                            <input type="text" id="projectGradient" placeholder="from-cyan-500 to-blue-500">
                        </div>
                        <div class="form-group">
                            <label>GitHub URL</label>
                            <input type="text" id="projectGithubUrl">
                        </div>
                        <div class="form-group">
                            <label>Demo URL</label>
                            <input type="text" id="projectDemoUrl">
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="projectIsFeatured"> Öne Çıkan Proje
                            </label>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="projectStatus" checked> Aktif (Yayınla)
                            </label>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="saveProject()">Kaydet</button>
                            <button onclick="cancelProjectForm()" style="background: #6c757d;">İptal</button>
                        </div>
                    </div>
                    <div id="projectsList"></div>
                </div>
                
                <div id="blog" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Blog Yazıları</h3>
                        <button onclick="showBlogForm()" style="width: auto; padding: 10px 20px;">+ Yeni Blog Yazısı Ekle</button>
                    </div>
                    <div id="blogForm" class="form-section" style="display: none; margin-bottom: 20px;">
                        <h4 id="blogFormTitle">Yeni Blog Yazısı Ekle</h4>
                        <div class="form-group">
                            <label>Başlık *</label>
                            <input type="text" id="blogTitle" required>
                        </div>
                        <div class="form-group">
                            <label>Özet *</label>
                            <textarea id="blogExcerpt" rows="3" required></textarea>
                        </div>
                        <div class="form-group">
                            <label>İçerik</label>
                            <textarea id="blogContent" rows="6"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Görsel URL</label>
                            <input type="text" id="blogImageUrl">
                        </div>
                        <div class="form-group">
                            <label>URL</label>
                            <input type="text" id="blogUrl" placeholder="blog-yazisi-url">
                        </div>
                        <div class="form-group">
                            <label>Kategori</label>
                            <input type="text" id="blogCategory">
                        </div>
                        <div class="form-group">
                            <label>Tarih</label>
                            <input type="date" id="blogDate">
                        </div>
                        <div class="form-group">
                            <label>Okuma Süresi</label>
                            <input type="text" id="blogReadTime" placeholder="5 min read">
                        </div>
                        <div class="form-group">
                            <label>Yazar</label>
                            <input type="text" id="blogAuthor">
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="blogIsFeatured"> Öne Çıkan Yazı
                            </label>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="blogIsPublished" checked> Yayınla
                            </label>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="saveBlog()">Kaydet</button>
                            <button onclick="cancelBlogForm()" style="background: #6c757d;">İptal</button>
                        </div>
                    </div>
                    <div id="blogList"></div>
                </div>
                
                <div id="messages" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>İletişim Mesajları</h3>
                        <span id="messagesCountBadge" style="background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px;">0 Mesaj</span>
                    </div>
                    <div id="messagesList"></div>
                </div>
                
                <!-- Message Detail Modal -->
                <div id="messageModal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Mesaj Detayı</h3>
                            <span class="close" onclick="closeMessageModal()">&times;</span>
                        </div>
                        <div class="modal-body" id="messageModalBody">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let authToken = null;
            
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const errorMsg = document.getElementById('errorMsg');
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'block';
                        document.getElementById('userName').textContent = data.user.username;
                        loadDashboard();
                    } else {
                        errorMsg.textContent = data.error || 'Giriş başarısız';
                        errorMsg.style.display = 'block';
                    }
                } catch (error) {
                    errorMsg.textContent = 'Bağlantı hatası';
                    errorMsg.style.display = 'block';
                }
            }
            
            async function logout() {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('dashboard').style.display = 'none';
            }
            
            async function checkAuth() {
                const response = await fetch('/api/auth/check', {
                    credentials: 'include'
                });
                const data = await response.json();
                
                if (data.authenticated) {
                    document.getElementById('loginForm').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                    document.getElementById('userName').textContent = data.user.username;
                    loadDashboard();
                }
            }
            
            function showTab(tabName, event) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                if (event && event.target) {
                    event.target.classList.add('active');
                }
                document.getElementById(tabName).classList.add('active');
                
                if (tabName === 'timeline') loadTimeline();
                if (tabName === 'skills') loadSkills();
                if (tabName === 'projects') loadProjects();
                if (tabName === 'blog') loadBlog();
                if (tabName === 'messages') loadMessages();
            }
            
            async function loadDashboard() {
                // Load stats
                const projects = await fetch('/api/projects', { credentials: 'include' }).then(r => r.json());
                const blog = await fetch('/api/blog', { credentials: 'include' }).then(r => r.json());
                const messages = await fetch('/api/contact/messages', { credentials: 'include' }).then(r => r.json());
                
                document.getElementById('projectsCount').textContent = projects.length || 0;
                document.getElementById('blogCount').textContent = blog.posts?.length || blog.length || 0;
                document.getElementById('messagesCount').textContent = messages.total || messages.messages?.length || 0;
                
                // Load user info
                const user = await fetch('/api/admin/user', { credentials: 'include' }).then(r => r.json());
                if (user) {
                    document.getElementById('fullName').value = user.full_name || '';
                    document.getElementById('userEmail').value = user.email || '';
                    document.getElementById('userPhone').value = user.phone || '';
                    document.getElementById('userLocation').value = user.location || '';
                    document.getElementById('userBio').value = user.bio || '';
                    
                    // Load profile image preview
                    if (user.profile_image_url) {
                        const img = document.getElementById('currentProfileImage');
                        // Normalize URL: remove localhost:5000 if present, use relative path
                        let imageUrl = user.profile_image_url;
                        if (imageUrl.includes('localhost:5000') || imageUrl.includes('127.0.0.1:5000')) {
                            imageUrl = imageUrl.replace(/https?:\/\/(localhost|127\.0\.0\.1):5000/, '');
                        }
                        if (!imageUrl.startsWith('/')) {
                            imageUrl = `/static/uploads/profiles/${imageUrl}`;
                        }
                        img.src = imageUrl;
                        img.style.display = 'block';
                    }
                }
                
                // Load profile info (for title)
                try {
                    const profile = await fetch('/api/profile', { credentials: 'include' }).then(r => r.json());
                    if (profile) {
                        document.getElementById('profileTitle').value = profile.title || '';
                    }
                } catch (error) {
                    console.error('Failed to load profile:', error);
                }
                
                // Load about section config
                try {
                    const about = await fetch('/api/about', { credentials: 'include' }).then(r => r.json());
                    if (about) {
                        document.getElementById('aboutTitle').value = about.title || '';
                        document.getElementById('aboutSubtitle').value = about.subtitle || '';
                        document.getElementById('aboutSkillsTitle').value = about.skills_title || '';
                    }
                } catch (error) {
                    console.error('Failed to load about section:', error);
                }
                
                // Load social links
                loadSocialLinks();
            }
            
            async function updateUserInfo() {
                const userData = {
                    full_name: document.getElementById('fullName').value,
                    email: document.getElementById('userEmail').value,
                    phone: document.getElementById('userPhone').value,
                    location: document.getElementById('userLocation').value,
                    bio: document.getElementById('userBio').value
                };
                
                const profileData = {
                    title: document.getElementById('profileTitle').value
                };
                
                // Update user info
                await fetch('/api/admin/user', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(userData)
                });
                
                // Update profile title
                await fetch('/api/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(profileData)
                });
                
                alert('Bilgiler güncellendi!');
            }
            
            async function uploadProfileImage() {
                const fileInput = document.getElementById('userProfileImage');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Lütfen bir dosya seçin!');
                    return;
                }
                
                // Check file size (16MB)
                if (file.size > 16 * 1024 * 1024) {
                    alert('Dosya boyutu 16MB dan büyük olamaz!');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/api/upload/profile-image', {
                        method: 'POST',
                        credentials: 'include',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Profil resmi başarıyla yüklendi!');
                        // Update preview
                        const img = document.getElementById('currentProfileImage');
                        // Normalize URL: remove localhost:5000 if present, use relative path
                        let imageUrl = data.url;
                        if (imageUrl && (imageUrl.includes('localhost:5000') || imageUrl.includes('127.0.0.1:5000'))) {
                            imageUrl = imageUrl.replace(/https?:\/\/(localhost|127\.0\.0\.1):5000/, '');
                        }
                        img.src = imageUrl || data.url;
                        img.style.display = 'block';
                        // Clear file input
                        fileInput.value = '';
                    } else {
                        alert(data.error || 'Yükleme başarısız!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                    console.error(error);
                }
            }
            
            async function deleteProfileImage() {
                if (!confirm('Profil resmini silmek istediğinize emin misiniz?')) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/upload/delete-profile-image', {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Profil resmi silindi!');
                        // Hide preview
                        const img = document.getElementById('currentProfileImage');
                        img.style.display = 'none';
                        img.src = '';
                    } else {
                        alert(data.error || 'Silme başarısız!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                    console.error(error);
                }
            }
            
            async function updateAboutSection() {
                const data = {
                    title: document.getElementById('aboutTitle').value,
                    subtitle: document.getElementById('aboutSubtitle').value,
                    skills_title: document.getElementById('aboutSkillsTitle').value
                };
                
                try {
                    const response = await fetch('/api/about', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('About section başlıkları güncellendi!');
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function changePassword() {
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                
                if (!newPassword || newPassword.length < 6) {
                    alert('Şifre en az 6 karakter olmalıdır!');
                    return;
                }
                
                if (newPassword !== confirmPassword) {
                    alert('Şifreler eşleşmiyor!');
                    return;
                }
                
                try {
                    const response = await fetch('/api/admin/user/password', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ password: newPassword })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Şifre başarıyla değiştirildi!');
                        document.getElementById('newPassword').value = '';
                        document.getElementById('confirmPassword').value = '';
                    } else {
                        alert(data.error || 'Şifre değiştirme başarısız!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                    console.error('Password change error:', error);
                }
            }
            
            let editingProjectId = null;
            let editingBlogId = null;
            let editingTimelineId = null;
            let editingSkillId = null;
            let editingSocialLinkId = null;
            
            // ==================== TIMELINE FUNCTIONS ====================
            
            function showTimelineForm(timelineId = null) {
                editingTimelineId = timelineId;
                const form = document.getElementById('timelineForm');
                const title = document.getElementById('timelineFormTitle');
                
                if (timelineId) {
                    title.textContent = 'Timeline Düzenle';
                    loadTimelineData(timelineId);
                } else {
                    title.textContent = 'Yeni Timeline Ekle';
                    document.getElementById('timelineYear').value = '';
                    document.getElementById('timelineTitle').value = '';
                    document.getElementById('timelineCompany').value = '';
                    document.getElementById('timelineDescription').value = '';
                    document.getElementById('timelineIconName').value = '';
                    document.getElementById('timelineSkills').value = '';
                    document.getElementById('timelineDisplayOrder').value = '0';
                }
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function cancelTimelineForm() {
                document.getElementById('timelineForm').style.display = 'none';
                editingTimelineId = null;
            }
            
            async function loadTimelineData(id) {
                const timeline = await fetch(`/api/timeline/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('timelineYear').value = timeline.year || '';
                document.getElementById('timelineTitle').value = timeline.title || '';
                document.getElementById('timelineCompany').value = timeline.company || '';
                document.getElementById('timelineDescription').value = timeline.description || '';
                document.getElementById('timelineIconName').value = timeline.icon_name || '';
                document.getElementById('timelineSkills').value = timeline.skills?.join(', ') || '';
                document.getElementById('timelineDisplayOrder').value = timeline.display_order || '0';
            }
            
            async function saveTimeline() {
                const data = {
                    year: document.getElementById('timelineYear').value,
                    title: document.getElementById('timelineTitle').value,
                    company: document.getElementById('timelineCompany').value,
                    description: document.getElementById('timelineDescription').value,
                    icon_name: document.getElementById('timelineIconName').value,
                    skills: document.getElementById('timelineSkills').value.split(',').map(s => s.trim()).filter(s => s),
                    display_order: parseInt(document.getElementById('timelineDisplayOrder').value) || 0
                };
                
                if (!data.year || !data.title || !data.company) {
                    alert('Yıl, başlık ve şirket zorunludur!');
                    return;
                }
                
                try {
                    const url = editingTimelineId ? `/api/timeline/${editingTimelineId}` : '/api/timeline';
                    const method = editingTimelineId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert(editingTimelineId ? 'Timeline güncellendi!' : 'Timeline eklendi!');
                        cancelTimelineForm();
                        loadTimeline();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function deleteTimeline(id) {
                if (!confirm('Bu timeline kaydını silmek istediğinize emin misiniz?')) return;
                
                try {
                    const response = await fetch(`/api/timeline/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        alert('Timeline silindi!');
                        loadTimeline();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadTimeline() {
                const timeline = await fetch('/api/timeline', { credentials: 'include' }).then(r => r.json());
                const list = document.getElementById('timelineList');
                if (timeline.length === 0) {
                    list.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">Henüz timeline kaydı eklenmemiş.</p>';
                } else {
                    let tableHTML = '<table class="timeline-table"><thead><tr><th>ID</th><th>Yıl</th><th>Başlık</th><th>Şirket</th><th>İşlemler</th></tr></thead><tbody>';
                    timeline.forEach(t => {
                        const title = (t.title || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const company = (t.company || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const year = (t.year || '').toString();
                        tableHTML += '<tr id="timeline-row-' + t.id + '">' +
                            '<td>' + t.id + '</td>' +
                            '<td>' + year + '</td>' +
                            '<td>' + title + '</td>' +
                            '<td>' + company + '</td>' +
                            '<td>' +
                                '<button class="btn-edit" onclick="toggleTimelineForm(' + t.id + ')" title="Düzenle"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                                '<button class="btn-danger" onclick="deleteTimeline(' + t.id + ')" title="Sil"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>' +
                            '</td>' +
                        '</tr>' +
                        '<tr class="accordion-row" id="timeline-accordion-' + t.id + '">' +
                            '<td colspan="5">' +
                                '<div class="accordion-content">' +
                                    '<div class="accordion-form">' +
                                        '<h4>Timeline Düzenle</h4>' +
                                        '<div class="form-group"><label>Yıl *</label><input type="text" id="timelineYear-' + t.id + '" placeholder="2018" required></div>' +
                                        '<div class="form-group"><label>Başlık (Pozisyon) *</label><input type="text" id="timelineTitle-' + t.id + '" placeholder="Frontend Developer" required></div>' +
                                        '<div class="form-group"><label>Şirket *</label><input type="text" id="timelineCompany-' + t.id + '" placeholder="StartupCo" required></div>' +
                                        '<div class="form-group"><label>Açıklama</label><textarea id="timelineDescription-' + t.id + '" rows="3" placeholder="Built responsive web applications..."></textarea></div>' +
                                        '<div class="form-group"><label>Icon Adı</label><input type="text" id="timelineIconName-' + t.id + '" placeholder="Code2, Server, Cloud, Rocket"></div>' +
                                        '<div class="form-group"><label>Yetenekler (virgülle ayırın)</label><input type="text" id="timelineSkills-' + t.id + '" placeholder="React, TypeScript, Tailwind CSS"></div>' +
                                        '<div class="form-group"><label>Sıralama</label><input type="number" id="timelineDisplayOrder-' + t.id + '" value="0"></div>' +
                                        '<div style="display: flex; gap: 10px;">' +
                                            '<button onclick="saveTimelineFromAccordion(' + t.id + ')">Kaydet</button>' +
                                            '<button onclick="toggleTimelineForm(' + t.id + ')" style="background: #6c757d;">İptal</button>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    list.innerHTML = tableHTML;
                }
            }
            
            function toggleTimelineForm(timelineId) {
                const accordion = document.getElementById('timeline-accordion-' + timelineId);
                if (!accordion) return;
                
                // Close all other accordions
                document.querySelectorAll('.accordion-row').forEach(row => {
                    if (row.id !== 'timeline-accordion-' + timelineId) {
                        row.classList.remove('active');
                    }
                });
                
                // Toggle current accordion
                if (accordion.classList.contains('active')) {
                    accordion.classList.remove('active');
                    editingTimelineId = null;
                } else {
                    accordion.classList.add('active');
                    editingTimelineId = timelineId;
                    loadTimelineDataToAccordion(timelineId);
                }
            }
            
            async function loadTimelineDataToAccordion(id) {
                const timeline = await fetch(`/api/timeline/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('timelineYear-' + id).value = timeline.year || '';
                document.getElementById('timelineTitle-' + id).value = timeline.title || '';
                document.getElementById('timelineCompany-' + id).value = timeline.company || '';
                document.getElementById('timelineDescription-' + id).value = timeline.description || '';
                document.getElementById('timelineIconName-' + id).value = timeline.icon_name || '';
                document.getElementById('timelineSkills-' + id).value = timeline.skills?.join(', ') || '';
                document.getElementById('timelineDisplayOrder-' + id).value = timeline.display_order || '0';
            }
            
            async function saveTimelineFromAccordion(id) {
                const data = {
                    year: document.getElementById('timelineYear-' + id).value,
                    title: document.getElementById('timelineTitle-' + id).value,
                    company: document.getElementById('timelineCompany-' + id).value,
                    description: document.getElementById('timelineDescription-' + id).value,
                    icon_name: document.getElementById('timelineIconName-' + id).value,
                    skills: document.getElementById('timelineSkills-' + id).value.split(',').map(s => s.trim()).filter(s => s),
                    display_order: parseInt(document.getElementById('timelineDisplayOrder-' + id).value) || 0
                };
                
                if (!data.year || !data.title || !data.company) {
                    alert('Yıl, başlık ve şirket zorunludur!');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/timeline/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('Timeline güncellendi!');
                        toggleTimelineForm(id);
                        loadTimeline();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            // ==================== SKILLS FUNCTIONS ====================
            
            function showSkillForm(skillId = null) {
                editingSkillId = skillId;
                const form = document.getElementById('skillForm');
                const title = document.getElementById('skillFormTitle');
                
                if (skillId) {
                    title.textContent = 'Yetenek Düzenle';
                    loadSkillData(skillId);
                } else {
                    title.textContent = 'Yeni Yetenek Ekle';
                    document.getElementById('skillName').value = '';
                    document.getElementById('skillLevel').value = '0';
                    document.getElementById('skillColor').value = 'cyan';
                    document.getElementById('skillDisplayOrder').value = '0';
                }
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function cancelSkillForm() {
                document.getElementById('skillForm').style.display = 'none';
                editingSkillId = null;
            }
            
            async function loadSkillData(id) {
                const skill = await fetch(`/api/skills/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('skillName').value = skill.name || '';
                document.getElementById('skillLevel').value = skill.level || '0';
                document.getElementById('skillColor').value = skill.color || 'cyan';
                document.getElementById('skillDisplayOrder').value = skill.display_order || '0';
            }
            
            async function saveSkill() {
                const data = {
                    name: document.getElementById('skillName').value,
                    level: parseInt(document.getElementById('skillLevel').value) || 0,
                    color: document.getElementById('skillColor').value,
                    display_order: parseInt(document.getElementById('skillDisplayOrder').value) || 0
                };
                
                if (!data.name || data.level < 0 || data.level > 100) {
                    alert('Yetenek adı zorunludur ve seviye 0-100 arasında olmalıdır!');
                    return;
                }
                
                try {
                    const url = editingSkillId ? `/api/skills/${editingSkillId}` : '/api/skills';
                    const method = editingSkillId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert(editingSkillId ? 'Yetenek güncellendi!' : 'Yetenek eklendi!');
                        cancelSkillForm();
                        loadSkills();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function deleteSkill(id) {
                if (!confirm('Bu yeteneği silmek istediğinize emin misiniz?')) return;
                
                try {
                    const response = await fetch(`/api/skills/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        alert('Yetenek silindi!');
                        loadSkills();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadSkills() {
                const skills = await fetch('/api/skills', { credentials: 'include' }).then(r => r.json());
                const list = document.getElementById('skillsList');
                if (skills.length === 0) {
                    list.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">Henüz yetenek eklenmemiş.</p>';
                } else {
                    let tableHTML = '<table class="skills-table"><thead><tr><th>ID</th><th>Yetenek</th><th>Seviye</th><th>Renk</th><th>İşlemler</th></tr></thead><tbody>';
                    skills.forEach(s => {
                        const name = (s.name || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const color = (s.color || '-').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        tableHTML += '<tr id="skill-row-' + s.id + '">' +
                            '<td>' + s.id + '</td>' +
                            '<td>' + name + '</td>' +
                            '<td>' + s.level + '%</td>' +
                            '<td>' + color + '</td>' +
                            '<td>' +
                                '<button class="btn-edit" onclick="toggleSkillForm(' + s.id + ')" title="Düzenle"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                                '<button class="btn-danger" onclick="deleteSkill(' + s.id + ')" title="Sil"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>' +
                            '</td>' +
                        '</tr>' +
                        '<tr class="accordion-row" id="skill-accordion-' + s.id + '">' +
                            '<td colspan="5">' +
                                '<div class="accordion-content">' +
                                    '<div class="accordion-form">' +
                                        '<h4>Yetenek Düzenle</h4>' +
                                        '<div class="form-group"><label>Yetenek Adı *</label><input type="text" id="skillName-' + s.id + '" placeholder="React & Next.js" required></div>' +
                                        '<div class="form-group"><label>Seviye (0-100) *</label><input type="number" id="skillLevel-' + s.id + '" min="0" max="100" value="0" required></div>' +
                                        '<div class="form-group"><label>Renk</label><select id="skillColor-' + s.id + '"><option value="cyan">Cyan</option><option value="purple">Purple</option><option value="pink">Pink</option></select></div>' +
                                        '<div class="form-group"><label>Sıralama</label><input type="number" id="skillDisplayOrder-' + s.id + '" value="0"></div>' +
                                        '<div style="display: flex; gap: 10px;">' +
                                            '<button onclick="saveSkillFromAccordion(' + s.id + ')">Kaydet</button>' +
                                            '<button onclick="toggleSkillForm(' + s.id + ')" style="background: #6c757d;">İptal</button>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    list.innerHTML = tableHTML;
                }
            }
            
            function toggleSkillForm(skillId) {
                const accordion = document.getElementById('skill-accordion-' + skillId);
                if (!accordion) return;
                
                document.querySelectorAll('.accordion-row').forEach(row => {
                    if (row.id !== 'skill-accordion-' + skillId) {
                        row.classList.remove('active');
                    }
                });
                
                if (accordion.classList.contains('active')) {
                    accordion.classList.remove('active');
                    editingSkillId = null;
                } else {
                    accordion.classList.add('active');
                    editingSkillId = skillId;
                    loadSkillDataToAccordion(skillId);
                }
            }
            
            async function loadSkillDataToAccordion(id) {
                const skill = await fetch(`/api/skills/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('skillName-' + id).value = skill.name || '';
                document.getElementById('skillLevel-' + id).value = skill.level || '0';
                document.getElementById('skillColor-' + id).value = skill.color || 'cyan';
                document.getElementById('skillDisplayOrder-' + id).value = skill.display_order || '0';
            }
            
            async function saveSkillFromAccordion(id) {
                const data = {
                    name: document.getElementById('skillName-' + id).value,
                    level: parseInt(document.getElementById('skillLevel-' + id).value) || 0,
                    color: document.getElementById('skillColor-' + id).value,
                    display_order: parseInt(document.getElementById('skillDisplayOrder-' + id).value) || 0
                };
                
                if (!data.name || data.level < 0 || data.level > 100) {
                    alert('Yetenek adı zorunludur ve seviye 0-100 arasında olmalıdır!');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/skills/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('Yetenek güncellendi!');
                        toggleSkillForm(id);
                        loadSkills();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            function showProjectForm(projectId = null) {
                editingProjectId = projectId;
                const form = document.getElementById('projectForm');
                const title = document.getElementById('projectFormTitle');
                
                if (projectId) {
                    title.textContent = 'Proje Düzenle';
                    loadProjectData(projectId);
                } else {
                    title.textContent = 'Yeni Proje Ekle';
                    document.getElementById('projectTitle').value = '';
                    document.getElementById('projectDescription').value = '';
                    document.getElementById('projectImageUrl').value = '';
                    document.getElementById('projectTags').value = '';
                    document.getElementById('projectIconName').value = '';
                    document.getElementById('projectGradient').value = '';
                    document.getElementById('projectGithubUrl').value = '';
                    document.getElementById('projectDemoUrl').value = '';
                    document.getElementById('projectIsFeatured').checked = false;
                    document.getElementById('projectStatus').checked = true;
                }
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function cancelProjectForm() {
                document.getElementById('projectForm').style.display = 'none';
                editingProjectId = null;
            }
            
            async function loadProjectData(id) {
                const project = await fetch(`/api/projects/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('projectTitle').value = project.title || '';
                document.getElementById('projectDescription').value = project.description || '';
                document.getElementById('projectImageUrl').value = project.image_url || '';
                document.getElementById('projectTags').value = project.tags?.join(', ') || '';
                document.getElementById('projectIconName').value = project.icon_name || '';
                document.getElementById('projectGradient').value = project.gradient || '';
                document.getElementById('projectGithubUrl').value = project.github_url || '';
                document.getElementById('projectDemoUrl').value = project.demo_url || '';
                document.getElementById('projectIsFeatured').checked = project.is_featured || false;
                document.getElementById('projectStatus').checked = project.status !== false;
            }
            
            async function saveProject() {
                const data = {
                    title: document.getElementById('projectTitle').value,
                    description: document.getElementById('projectDescription').value,
                    image_url: document.getElementById('projectImageUrl').value,
                    tags: document.getElementById('projectTags').value.split(',').map(t => t.trim()).filter(t => t),
                    icon_name: document.getElementById('projectIconName').value,
                    gradient: document.getElementById('projectGradient').value,
                    github_url: document.getElementById('projectGithubUrl').value,
                    demo_url: document.getElementById('projectDemoUrl').value,
                    is_featured: document.getElementById('projectIsFeatured').checked,
                    status: document.getElementById('projectStatus').checked
                };
                
                if (!data.title || !data.description) {
                    alert('Başlık ve açıklama zorunludur!');
                    return;
                }
                
                try {
                    const url = editingProjectId ? `/api/projects/${editingProjectId}` : '/api/projects';
                    const method = editingProjectId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert(editingProjectId ? 'Proje güncellendi!' : 'Proje eklendi!');
                        cancelProjectForm();
                        loadProjects();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function deleteProject(id) {
                if (!confirm('Bu projeyi silmek istediğinize emin misiniz?')) return;
                
                try {
                    const response = await fetch(`/api/projects/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        alert('Proje silindi!');
                        loadProjects();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadProjects() {
                const projects = await fetch('/api/projects?status=all', { credentials: 'include' }).then(r => r.json());
                const list = document.getElementById('projectsList');
                if (projects.length === 0) {
                    list.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">Henüz proje eklenmemiş.</p>';
                } else {
                    let tableHTML = '<table class="projects-table"><thead><tr><th>ID</th><th>Başlık</th><th>Açıklama</th><th>İşlemler</th></tr></thead><tbody>';
                    projects.forEach(p => {
                        const title = (p.title || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const desc = (p.description || '').substring(0, 80).replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const displayDesc = p.description && p.description.length > 80 ? desc + '...' : desc;
                        tableHTML += '<tr id="project-row-' + p.id + '">' +
                            '<td>' + p.id + '</td>' +
                            '<td>' + title + '</td>' +
                            '<td>' + displayDesc + '</td>' +
                            '<td>' +
                                '<button class="btn-edit" onclick="toggleProjectForm(' + p.id + ')" title="Düzenle"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                                '<button class="btn-danger" onclick="deleteProject(' + p.id + ')" title="Sil"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>' +
                            '</td>' +
                        '</tr>' +
                        '<tr class="accordion-row" id="project-accordion-' + p.id + '">' +
                            '<td colspan="4">' +
                                '<div class="accordion-content">' +
                                    '<div class="accordion-form">' +
                                        '<h4>Proje Düzenle</h4>' +
                                        '<div class="form-group"><label>Başlık *</label><input type="text" id="projectTitle-' + p.id + '" required></div>' +
                                        '<div class="form-group"><label>Açıklama *</label><textarea id="projectDescription-' + p.id + '" rows="3" required></textarea></div>' +
                                        '<div class="form-group"><label>Görsel URL</label><input type="text" id="projectImageUrl-' + p.id + '"></div>' +
                                        '<div class="form-group"><label>Etiketler (virgülle ayırın)</label><input type="text" id="projectTags-' + p.id + '" placeholder="React, Node.js, MongoDB"></div>' +
                                        '<div class="form-group"><label>Icon Adı</label><input type="text" id="projectIconName-' + p.id + '" placeholder="Cloud, Database, etc."></div>' +
                                        '<div class="form-group"><label>Gradient</label><input type="text" id="projectGradient-' + p.id + '" placeholder="from-cyan-500 to-blue-500"></div>' +
                                        '<div class="form-group"><label>GitHub URL</label><input type="text" id="projectGithubUrl-' + p.id + '"></div>' +
                                        '<div class="form-group"><label>Demo URL</label><input type="text" id="projectDemoUrl-' + p.id + '"></div>' +
                                        '<div class="form-group"><label><input type="checkbox" id="projectIsFeatured-' + p.id + '"> Öne Çıkan Proje</label></div>' +
                                        '<div class="form-group"><label><input type="checkbox" id="projectStatus-' + p.id + '" checked> Aktif (Yayınla)</label></div>' +
                                        '<div style="display: flex; gap: 10px;">' +
                                            '<button onclick="saveProjectFromAccordion(' + p.id + ')">Kaydet</button>' +
                                            '<button onclick="toggleProjectForm(' + p.id + ')" style="background: #6c757d;">İptal</button>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    list.innerHTML = tableHTML;
                }
            }
            
            function toggleProjectForm(projectId) {
                const accordion = document.getElementById('project-accordion-' + projectId);
                if (!accordion) return;
                
                document.querySelectorAll('.accordion-row').forEach(row => {
                    if (row.id !== 'project-accordion-' + projectId) {
                        row.classList.remove('active');
                    }
                });
                
                if (accordion.classList.contains('active')) {
                    accordion.classList.remove('active');
                    editingProjectId = null;
                } else {
                    accordion.classList.add('active');
                    editingProjectId = projectId;
                    loadProjectDataToAccordion(projectId);
                }
            }
            
            async function loadProjectDataToAccordion(id) {
                const project = await fetch(`/api/projects/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('projectTitle-' + id).value = project.title || '';
                document.getElementById('projectDescription-' + id).value = project.description || '';
                document.getElementById('projectImageUrl-' + id).value = project.image_url || '';
                document.getElementById('projectTags-' + id).value = project.tags?.join(', ') || '';
                document.getElementById('projectIconName-' + id).value = project.icon_name || '';
                document.getElementById('projectGradient-' + id).value = project.gradient || '';
                document.getElementById('projectGithubUrl-' + id).value = project.github_url || '';
                document.getElementById('projectDemoUrl-' + id).value = project.demo_url || '';
                document.getElementById('projectIsFeatured-' + id).checked = project.is_featured || false;
                document.getElementById('projectStatus-' + id).checked = project.status !== false;
            }
            
            async function saveProjectFromAccordion(id) {
                const data = {
                    title: document.getElementById('projectTitle-' + id).value,
                    description: document.getElementById('projectDescription-' + id).value,
                    image_url: document.getElementById('projectImageUrl-' + id).value,
                    tags: document.getElementById('projectTags-' + id).value.split(',').map(t => t.trim()).filter(t => t),
                    icon_name: document.getElementById('projectIconName-' + id).value,
                    gradient: document.getElementById('projectGradient-' + id).value,
                    github_url: document.getElementById('projectGithubUrl-' + id).value,
                    demo_url: document.getElementById('projectDemoUrl-' + id).value,
                    is_featured: document.getElementById('projectIsFeatured-' + id).checked,
                    status: document.getElementById('projectStatus-' + id).checked
                };
                
                if (!data.title || !data.description) {
                    alert('Başlık ve açıklama zorunludur!');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/projects/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('Proje güncellendi!');
                        toggleProjectForm(id);
                        loadProjects();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            function showBlogForm(blogId = null) {
                editingBlogId = blogId;
                const form = document.getElementById('blogForm');
                const title = document.getElementById('blogFormTitle');
                
                if (blogId) {
                    title.textContent = 'Blog Yazısı Düzenle';
                    loadBlogData(blogId);
                } else {
                    title.textContent = 'Yeni Blog Yazısı Ekle';
                    document.getElementById('blogTitle').value = '';
                    document.getElementById('blogExcerpt').value = '';
                    document.getElementById('blogContent').value = '';
                    document.getElementById('blogImageUrl').value = '';
                    document.getElementById('blogUrl').value = '';
                    document.getElementById('blogCategory').value = '';
                    document.getElementById('blogDate').value = '';
                    document.getElementById('blogReadTime').value = '';
                    document.getElementById('blogAuthor').value = '';
                    document.getElementById('blogIsFeatured').checked = false;
                    document.getElementById('blogIsPublished').checked = true;
                }
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function cancelBlogForm() {
                document.getElementById('blogForm').style.display = 'none';
                editingBlogId = null;
            }
            
            async function loadBlogData(id) {
                const post = await fetch(`/api/blog/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('blogTitle').value = post.title || '';
                document.getElementById('blogExcerpt').value = post.excerpt || '';
                document.getElementById('blogContent').value = post.content || '';
                document.getElementById('blogImageUrl').value = post.image_url || '';
                document.getElementById('blogUrl').value = post.url || '';
                document.getElementById('blogCategory').value = post.category || '';
                if (post.date) {
                    const date = new Date(post.date);
                    document.getElementById('blogDate').value = date.toISOString().split('T')[0];
                }
                document.getElementById('blogReadTime').value = post.read_time || '';
                document.getElementById('blogAuthor').value = post.author || '';
                document.getElementById('blogIsFeatured').checked = post.is_featured || false;
                document.getElementById('blogIsPublished').checked = post.is_published !== false;
            }
            
            async function saveBlog() {
                const data = {
                    title: document.getElementById('blogTitle').value,
                    excerpt: document.getElementById('blogExcerpt').value,
                    content: document.getElementById('blogContent').value,
                    image_url: document.getElementById('blogImageUrl').value,
                    url: document.getElementById('blogUrl').value,
                    category: document.getElementById('blogCategory').value,
                    date: document.getElementById('blogDate').value || new Date().toISOString(),
                    read_time: document.getElementById('blogReadTime').value,
                    author: document.getElementById('blogAuthor').value,
                    is_featured: document.getElementById('blogIsFeatured').checked,
                    is_published: document.getElementById('blogIsPublished').checked
                };
                
                if (!data.title || !data.excerpt) {
                    alert('Başlık ve özet zorunludur!');
                    return;
                }
                
                try {
                    const url = editingBlogId ? `/api/blog/${editingBlogId}` : '/api/blog';
                    const method = editingBlogId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert(editingBlogId ? 'Blog yazısı güncellendi!' : 'Blog yazısı eklendi!');
                        cancelBlogForm();
                        loadBlog();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function deleteBlog(id) {
                if (!confirm('Bu blog yazısını silmek istediğinize emin misiniz?')) return;
                
                try {
                    const response = await fetch(`/api/blog/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        alert('Blog yazısı silindi!');
                        loadBlog();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadBlog() {
                const blog = await fetch('/api/blog?per_page=100&all=true', { credentials: 'include' }).then(r => r.json());
                const posts = blog.posts || blog;
                const list = document.getElementById('blogList');
                if (posts.length === 0) {
                    list.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">Henüz blog yazısı eklenmemiş.</p>';
                } else {
                    let tableHTML = '<table class="blog-table"><thead><tr><th>ID</th><th>Başlık</th><th>Kategori</th><th>Tarih</th><th>İşlemler</th></tr></thead><tbody>';
                    posts.forEach(p => {
                        const date = p.date ? new Date(p.date).toLocaleDateString('tr-TR') : '-';
                        const title = (p.title || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const category = (p.category || '-').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        tableHTML += '<tr id="blog-row-' + p.id + '">' +
                            '<td>' + p.id + '</td>' +
                            '<td>' + title + '</td>' +
                            '<td>' + category + '</td>' +
                            '<td style="color: #666; font-size: 13px;">' + date + '</td>' +
                            '<td>' +
                                '<button class="btn-edit" onclick="toggleBlogForm(' + p.id + ')" title="Düzenle"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                                '<button class="btn-danger" onclick="deleteBlog(' + p.id + ')" title="Sil"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>' +
                            '</td>' +
                        '</tr>' +
                        '<tr class="accordion-row" id="blog-accordion-' + p.id + '">' +
                            '<td colspan="5">' +
                                '<div class="accordion-content">' +
                                    '<div class="accordion-form">' +
                                        '<h4>Blog Yazısı Düzenle</h4>' +
                                        '<div class="form-group"><label>Başlık *</label><input type="text" id="blogTitle-' + p.id + '" required></div>' +
                                        '<div class="form-group"><label>Özet *</label><textarea id="blogExcerpt-' + p.id + '" rows="3" required></textarea></div>' +
                                        '<div class="form-group"><label>İçerik</label><textarea id="blogContent-' + p.id + '" rows="6"></textarea></div>' +
                                        '<div class="form-group"><label>Görsel URL</label><input type="text" id="blogImageUrl-' + p.id + '"></div>' +
                                        '<div class="form-group"><label>URL</label><input type="text" id="blogUrl-' + p.id + '" placeholder="blog-yazisi-url"></div>' +
                                        '<div class="form-group"><label>Kategori</label><input type="text" id="blogCategory-' + p.id + '"></div>' +
                                        '<div class="form-group"><label>Tarih</label><input type="date" id="blogDate-' + p.id + '"></div>' +
                                        '<div class="form-group"><label>Okuma Süresi</label><input type="text" id="blogReadTime-' + p.id + '" placeholder="5 min read"></div>' +
                                        '<div class="form-group"><label>Yazar</label><input type="text" id="blogAuthor-' + p.id + '"></div>' +
                                        '<div class="form-group"><label><input type="checkbox" id="blogIsFeatured-' + p.id + '"> Öne Çıkan Yazı</label></div>' +
                                        '<div class="form-group"><label><input type="checkbox" id="blogIsPublished-' + p.id + '" checked> Yayınla</label></div>' +
                                        '<div style="display: flex; gap: 10px;">' +
                                            '<button onclick="saveBlogFromAccordion(' + p.id + ')">Kaydet</button>' +
                                            '<button onclick="toggleBlogForm(' + p.id + ')" style="background: #6c757d;">İptal</button>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    list.innerHTML = tableHTML;
                }
            }
            
            function toggleBlogForm(blogId) {
                const accordion = document.getElementById('blog-accordion-' + blogId);
                if (!accordion) return;
                
                document.querySelectorAll('.accordion-row').forEach(row => {
                    if (row.id !== 'blog-accordion-' + blogId) {
                        row.classList.remove('active');
                    }
                });
                
                if (accordion.classList.contains('active')) {
                    accordion.classList.remove('active');
                    editingBlogId = null;
                } else {
                    accordion.classList.add('active');
                    editingBlogId = blogId;
                    loadBlogDataToAccordion(blogId);
                }
            }
            
            async function loadBlogDataToAccordion(id) {
                const post = await fetch(`/api/blog/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('blogTitle-' + id).value = post.title || '';
                document.getElementById('blogExcerpt-' + id).value = post.excerpt || '';
                document.getElementById('blogContent-' + id).value = post.content || '';
                document.getElementById('blogImageUrl-' + id).value = post.image_url || '';
                document.getElementById('blogUrl-' + id).value = post.url || '';
                document.getElementById('blogCategory-' + id).value = post.category || '';
                if (post.date) {
                    const date = new Date(post.date);
                    document.getElementById('blogDate-' + id).value = date.toISOString().split('T')[0];
                }
                document.getElementById('blogReadTime-' + id).value = post.read_time || '';
                document.getElementById('blogAuthor-' + id).value = post.author || '';
                document.getElementById('blogIsFeatured-' + id).checked = post.is_featured || false;
                document.getElementById('blogIsPublished-' + id).checked = post.is_published !== false;
            }
            
            async function saveBlogFromAccordion(id) {
                const data = {
                    title: document.getElementById('blogTitle-' + id).value,
                    excerpt: document.getElementById('blogExcerpt-' + id).value,
                    content: document.getElementById('blogContent-' + id).value,
                    image_url: document.getElementById('blogImageUrl-' + id).value,
                    url: document.getElementById('blogUrl-' + id).value,
                    category: document.getElementById('blogCategory-' + id).value,
                    date: document.getElementById('blogDate-' + id).value || new Date().toISOString(),
                    read_time: document.getElementById('blogReadTime-' + id).value,
                    author: document.getElementById('blogAuthor-' + id).value,
                    is_featured: document.getElementById('blogIsFeatured-' + id).checked,
                    is_published: document.getElementById('blogIsPublished-' + id).checked
                };
                
                if (!data.title || !data.excerpt) {
                    alert('Başlık ve özet zorunludur!');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/blog/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('Blog yazısı güncellendi!');
                        toggleBlogForm(id);
                        loadBlog();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadMessages() {
                const messages = await fetch('/api/contact/messages?per_page=100', { credentials: 'include' }).then(r => r.json());
                const msgs = messages.messages || messages;
                const list = document.getElementById('messagesList');
                const countBadge = document.getElementById('messagesCountBadge');
                
                if (countBadge) {
                    countBadge.textContent = msgs.length + ' Mesaj';
                }
                
                if (msgs.length === 0) {
                    list.innerHTML = '<p style="text-align: center; padding: 40px; color: #666; background: #f8f9fa; border-radius: 8px;">Henüz mesaj bulunmuyor.</p>';
                    return;
                }
                
                let tableHTML = '<table class="messages-table"><thead><tr><th>ID</th><th>İsim</th><th>E-posta</th><th>Konu</th><th>Mesaj</th><th>Tarih</th></tr></thead><tbody>';
                
                msgs.forEach(m => {
                    const messagePreview = (m.message.length > 80 ? m.message.substring(0, 80) + '...' : m.message).replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                    const date = new Date(m.created_at);
                    const formattedDate = date.toLocaleDateString('tr-TR', { 
                        year: 'numeric', 
                        month: '2-digit', 
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    const name = (m.name || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                    const email = (m.email || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                    const subject = (m.subject || '<span style="color: #999; font-style: italic;">Konu yok</span>').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                    
                    tableHTML += '<tr>' +
                        '<td style="font-weight: 600; color: #667eea;">' + m.id + '</td>' +
                        '<td style="font-weight: 500;">' + name + '</td>' +
                        '<td><a href="mailto:' + email + '" style="color: #667eea; text-decoration: none;">' + email + '</a></td>' +
                        '<td>' + subject + '</td>' +
                        '<td><span class="message-preview" onclick="showMessageDetail(' + m.id + ')" title="Detayları görmek için tıklayın">' + messagePreview + '</span></td>' +
                        '<td style="color: #666; font-size: 13px;">' + formattedDate + '</td>' +
                    '</tr>';
                });
                
                tableHTML += '</tbody></table>';
                list.innerHTML = tableHTML;
                
                // Store messages globally for modal
                window.messagesData = msgs;
            }
            
            function showMessageDetail(messageId) {
                const message = window.messagesData.find(m => m.id === messageId);
                if (!message) return;
                
                const modal = document.getElementById('messageModal');
                const modalBody = document.getElementById('messageModalBody');
                
                const date = new Date(message.created_at);
                const formattedDate = date.toLocaleDateString('tr-TR', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const msgId = message.id;
                const msgName = (message.name || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;').replace(/\\n/g, '<br>');
                const msgEmail = (message.email || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                const msgSubject = (message.subject || 'Konu belirtilmemiş').replace(/'/g, '&#39;').replace(/"/g, '&quot;').replace(/\\n/g, '<br>');
                const msgMessage = (message.message || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;').replace(/\\n/g, '<br>');
                
                modalBody.innerHTML = 
                    '<div class="modal-field">' +
                        '<label>ID</label>' +
                        '<p>' + msgId + '</p>' +
                    '</div>' +
                    '<div class="modal-field">' +
                        '<label>İsim</label>' +
                        '<p>' + msgName + '</p>' +
                    '</div>' +
                    '<div class="modal-field">' +
                        '<label>E-posta</label>' +
                        '<p><a href="mailto:' + msgEmail + '" style="color: #667eea; text-decoration: none;">' + msgEmail + '</a></p>' +
                    '</div>' +
                    '<div class="modal-field">' +
                        '<label>Konu</label>' +
                        '<p>' + msgSubject + '</p>' +
                    '</div>' +
                    '<div class="modal-field">' +
                        '<label>Mesaj</label>' +
                        '<p style="white-space: pre-wrap; line-height: 1.8;">' + msgMessage + '</p>' +
                    '</div>' +
                    '<div class="modal-field">' +
                        '<label>Tarih</label>' +
                        '<p>' + formattedDate + '</p>' +
                    '</div>';
                
                modal.style.display = 'block';
            }
            
            function closeMessageModal() {
                document.getElementById('messageModal').style.display = 'none';
            }
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('messageModal');
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            }
            
            // ==================== SOCIAL LINKS FUNCTIONS ====================
            
            function showSocialLinkForm(linkId = null) {
                editingSocialLinkId = linkId;
                const form = document.getElementById('socialLinkForm');
                const title = document.getElementById('socialLinkFormTitle');
                
                if (linkId) {
                    title.textContent = 'Sosyal Medya Linki Düzenle';
                    loadSocialLinkData(linkId);
                } else {
                    title.textContent = 'Yeni Sosyal Medya Linki Ekle';
                    document.getElementById('socialLinkPlatform').value = '';
                    document.getElementById('socialLinkUrl').value = '';
                    document.getElementById('socialLinkIconName').value = '';
                    document.getElementById('socialLinkDisplayOrder').value = '0';
                }
                form.style.display = 'block';
                form.scrollIntoView({ behavior: 'smooth' });
            }
            
            function cancelSocialLinkForm() {
                document.getElementById('socialLinkForm').style.display = 'none';
                editingSocialLinkId = null;
            }
            
            async function loadSocialLinkData(id) {
                const link = await fetch(`/api/user/social-links/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('socialLinkPlatform').value = link.platform || '';
                document.getElementById('socialLinkUrl').value = link.url || '';
                document.getElementById('socialLinkIconName').value = link.icon_name || '';
                document.getElementById('socialLinkDisplayOrder').value = link.display_order || '0';
            }
            
            async function saveSocialLink() {
                const data = {
                    platform: document.getElementById('socialLinkPlatform').value,
                    url: document.getElementById('socialLinkUrl').value,
                    icon_name: document.getElementById('socialLinkIconName').value,
                    display_order: parseInt(document.getElementById('socialLinkDisplayOrder').value) || 0
                };
                
                if (!data.platform || !data.url) {
                    alert('Platform ve URL zorunludur!');
                    return;
                }
                
                try {
                    const url = editingSocialLinkId ? `/api/user/social-links/${editingSocialLinkId}` : '/api/user/social-links';
                    const method = editingSocialLinkId ? 'PUT' : 'POST';
                    
                    const response = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert(editingSocialLinkId ? 'Sosyal medya linki güncellendi!' : 'Sosyal medya linki eklendi!');
                        cancelSocialLinkForm();
                        loadSocialLinks();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function deleteSocialLink(id) {
                if (!confirm('Bu sosyal medya linkini silmek istediğinize emin misiniz?')) return;
                
                try {
                    const response = await fetch(`/api/user/social-links/${id}`, {
                        method: 'DELETE',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        alert('Sosyal medya linki silindi!');
                        loadSocialLinks();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            async function loadSocialLinks() {
                const links = await fetch('/api/user/social-links', { credentials: 'include' }).then(r => r.json());
                const list = document.getElementById('socialLinksList');
                if (links.length === 0) {
                    list.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">Henüz sosyal medya linki eklenmemiş.</p>';
                } else {
                    let tableHTML = '<table class="social-links-table"><thead><tr><th>ID</th><th>Platform</th><th>URL</th><th>Icon</th><th>İşlemler</th></tr></thead><tbody>';
                    links.forEach(link => {
                        const platform = (link.platform || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const url = (link.url || '').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const iconName = (link.icon_name || '-').replace(/'/g, '&#39;').replace(/"/g, '&quot;');
                        const displayUrl = url.length > 50 ? url.substring(0, 50) + '...' : url;
                        tableHTML += '<tr id="socialLink-row-' + link.id + '">' +
                            '<td>' + link.id + '</td>' +
                            '<td>' + platform + '</td>' +
                            '<td><a href="' + url + '" target="_blank" style="color: #06b6d4; text-decoration: none;">' + displayUrl + '</a></td>' +
                            '<td>' + iconName + '</td>' +
                            '<td>' +
                                '<button class="btn-edit" onclick="toggleSocialLinkForm(' + link.id + ')" title="Düzenle"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>' +
                                '<button class="btn-danger" onclick="deleteSocialLink(' + link.id + ')" title="Sil"><svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>' +
                            '</td>' +
                        '</tr>' +
                        '<tr class="accordion-row" id="socialLink-accordion-' + link.id + '">' +
                            '<td colspan="5">' +
                                '<div class="accordion-content">' +
                                    '<div class="accordion-form">' +
                                        '<h4>Sosyal Medya Linki Düzenle</h4>' +
                                        '<div class="form-group"><label>Platform *</label><input type="text" id="socialLinkPlatform-' + link.id + '" placeholder="GitHub, LinkedIn, Twitter, etc." required></div>' +
                                        '<div class="form-group"><label>URL *</label><input type="text" id="socialLinkUrl-' + link.id + '" placeholder="https://github.com/username" required></div>' +
                                        '<div class="form-group"><label>Icon Adı (Lucide Icons)</label><input type="text" id="socialLinkIconName-' + link.id + '" placeholder="Github, Linkedin, Twitter"></div>' +
                                        '<div class="form-group"><label>Sıralama</label><input type="number" id="socialLinkDisplayOrder-' + link.id + '" value="0"></div>' +
                                        '<div style="display: flex; gap: 10px;">' +
                                            '<button onclick="saveSocialLinkFromAccordion(' + link.id + ')">Kaydet</button>' +
                                            '<button onclick="toggleSocialLinkForm(' + link.id + ')" style="background: #6c757d;">İptal</button>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' +
                            '</td>' +
                        '</tr>';
                    });
                    tableHTML += '</tbody></table>';
                    list.innerHTML = tableHTML;
                }
            }
            
            function toggleSocialLinkForm(linkId) {
                const accordion = document.getElementById('socialLink-accordion-' + linkId);
                if (!accordion) return;
                
                document.querySelectorAll('.accordion-row').forEach(row => {
                    if (row.id !== 'socialLink-accordion-' + linkId) {
                        row.classList.remove('active');
                    }
                });
                
                if (accordion.classList.contains('active')) {
                    accordion.classList.remove('active');
                    editingSocialLinkId = null;
                } else {
                    accordion.classList.add('active');
                    editingSocialLinkId = linkId;
                    loadSocialLinkDataToAccordion(linkId);
                }
            }
            
            async function loadSocialLinkDataToAccordion(id) {
                const link = await fetch(`/api/user/social-links/${id}`, { credentials: 'include' }).then(r => r.json());
                document.getElementById('socialLinkPlatform-' + id).value = link.platform || '';
                document.getElementById('socialLinkUrl-' + id).value = link.url || '';
                document.getElementById('socialLinkIconName-' + id).value = link.icon_name || '';
                document.getElementById('socialLinkDisplayOrder-' + id).value = link.display_order || '0';
            }
            
            async function saveSocialLinkFromAccordion(id) {
                const data = {
                    platform: document.getElementById('socialLinkPlatform-' + id).value,
                    url: document.getElementById('socialLinkUrl-' + id).value,
                    icon_name: document.getElementById('socialLinkIconName-' + id).value,
                    display_order: parseInt(document.getElementById('socialLinkDisplayOrder-' + id).value) || 0
                };
                
                if (!data.platform || !data.url) {
                    alert('Platform ve URL zorunludur!');
                    return;
                }
                
                try {
                    const response = await fetch(`/api/user/social-links/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        alert('Sosyal medya linki güncellendi!');
                        toggleSocialLinkForm(id);
                        loadSocialLinks();
                    } else {
                        alert('Hata oluştu!');
                    }
                } catch (error) {
                    alert('Bağlantı hatası!');
                }
            }
            
            // Check auth on page load
            checkAuth();
        </script>
    </body>
    </html>
    """
    return render_template_string(admin_html)

@app.route('/api/user', methods=['GET'])
def get_public_user_info():
    """Get public user information (project owner)"""
    user = User.query.first()  # Get the only user (project owner)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's social links
    social_links = UserSocialLink.query.filter_by(user_id=user.id).order_by(UserSocialLink.display_order).all()
    
    # Build profile image URL if exists
    profile_image_url = None
    if user.profile_image_url:
        # If it's already a full path, use it; otherwise construct it
        if user.profile_image_url.startswith('/static/'):
            profile_image_url = user.profile_image_url
        else:
            profile_image_url = f"/static/uploads/profiles/{user.profile_image_url}"
    
    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'bio': user.bio,
        'location': user.location,
        'profile_image_url': normalize_image_url(profile_image_url),
        'social_links': [{
            'id': link.id,
            'platform': link.platform,
            'url': link.url,
            'icon_name': link.icon_name,
            'display_order': link.display_order
        } for link in social_links]
    })

@app.route('/api/admin/user', methods=['GET'])
@login_required
def get_user_info():
    """Get current user information (admin)"""
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'bio': user.bio,
        'location': user.location,
        'profile_image_url': user.profile_image_url
    })

@app.route('/api/admin/user', methods=['PUT'])
@login_required
def update_user_info():
    """Update user information"""
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.bio = data.get('bio', user.bio)
    user.location = data.get('location', user.location)
    user.profile_image_url = data.get('profile_image_url', user.profile_image_url)
    user.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'User information updated'}), 200

@app.route('/api/admin/user/password', methods=['PUT'])
@login_required
def change_password():
    """Change user password"""
    user = User.query.get(session['user_id'])
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Şifre en az 6 karakter olmalıdır'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Şifre başarıyla güncellendi'}), 200

# ==================== USER SOCIAL LINKS ROUTES ====================

@app.route('/api/user/social-links', methods=['GET'])
def get_user_social_links():
    """Get user's social links"""
    user = User.query.first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    links = UserSocialLink.query.filter_by(user_id=user.id).order_by(UserSocialLink.display_order).all()
    
    return jsonify([{
        'id': link.id,
        'platform': link.platform,
        'url': link.url,
        'icon_name': link.icon_name,
        'display_order': link.display_order
    } for link in links])

@app.route('/api/user/social-links', methods=['POST'])
@login_required
def create_user_social_link():
    """Create a new user social link"""
    user = User.query.first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    link = UserSocialLink(
        user_id=user.id,
        platform=data.get('platform'),
        url=data.get('url'),
        icon_name=data.get('icon_name'),
        display_order=data.get('display_order', 0)
    )
    
    db.session.add(link)
    db.session.commit()
    
    return jsonify({'message': 'Social link created', 'id': link.id}), 201

@app.route('/api/user/social-links/<int:id>', methods=['GET'])
def get_user_social_link(id):
    """Get a single user social link"""
    link = UserSocialLink.query.get_or_404(id)
    
    return jsonify({
        'id': link.id,
        'platform': link.platform,
        'url': link.url,
        'icon_name': link.icon_name,
        'display_order': link.display_order
    })

@app.route('/api/user/social-links/<int:id>', methods=['PUT'])
@login_required
def update_user_social_link(id):
    """Update a user social link"""
    link = UserSocialLink.query.get_or_404(id)
    data = request.get_json()
    
    link.platform = data.get('platform', link.platform)
    link.url = data.get('url', link.url)
    link.icon_name = data.get('icon_name', link.icon_name)
    link.display_order = data.get('display_order', link.display_order)
    link.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'message': 'Social link updated'}), 200

@app.route('/api/user/social-links/<int:id>', methods=['DELETE'])
@login_required
def delete_user_social_link(id):
    """Delete a user social link"""
    link = UserSocialLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'message': 'Social link deleted'}), 200

# ==================== FILE UPLOAD ROUTES ====================

@app.route('/api/upload/profile-image', methods=['POST'])
@login_required
def upload_profile_image():
    """Upload a profile image for the user"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        if not file:
            return jsonify({'error': 'File upload failed'}), 500
        
        user = User.query.first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete old profile image if exists
        if user.profile_image_url:
            # Normalize old filename: extract just the filename if it's a full path
            old_filename = user.profile_image_url
            if '/' in old_filename:
                old_filename = old_filename.split('/')[-1]
            
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', old_filename)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError as e:
                    app.logger.warning(f'Could not delete old profile image: {e}')
        
        # Ensure profiles directory exists
        profiles_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles')
        os.makedirs(profiles_dir, exist_ok=True)
        
        # Save new file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(profiles_dir, unique_filename)
        
        try:
            file.save(file_path)
        except Exception as e:
            app.logger.error(f'Error saving file: {e}')
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        
        user.profile_image_url = unique_filename
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(f'Error committing to database: {e}')
            # Try to delete the uploaded file if database commit fails
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            return jsonify({'error': f'Failed to update database: {str(e)}'}), 500
        
        return jsonify({
            'message': 'Profile image uploaded successfully',
            'url': f'/static/uploads/profiles/{unique_filename}'
        }), 200
    
    except Exception as e:
        app.logger.error(f'Unexpected error in upload_profile_image: {e}', exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/upload/delete-profile-image', methods=['DELETE'])
@login_required
def delete_profile_image():
    """Delete the user's profile image"""
    user = User.query.first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.profile_image_url:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', user.profile_image_url)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Ignore if file doesn't exist
        
        user.profile_image_url = None
        db.session.commit()
        return jsonify({'message': 'Profile image deleted successfully'}), 200
    
    return jsonify({'message': 'No profile image to delete'}), 200

@app.route('/static/uploads/profiles/<filename>')
def uploaded_profile_file(filename):
    """Serve uploaded profile images"""
    from flask import Response
    response = send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), filename)
    # Add CORS headers for static files - allow all origins since these are public images
    # In production, you might want to restrict this to specific domains
    origin = request.headers.get('Origin')
    if origin and origin in app.config['CORS_ORIGINS']:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
