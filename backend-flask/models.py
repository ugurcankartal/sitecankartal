from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User/Admin model - Only one user allowed (project owner)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Personal information
    full_name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    profile_image_url = Column(String(500), nullable=True)  # Profile image URL
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    social_links = relationship('UserSocialLink', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    """Profile information for hero section"""
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    social_links = relationship('SocialLink', backref='profile', lazy=True, cascade='all, delete-orphan')

class SocialLink(db.Model):
    """Social media links for Profile"""
    __tablename__ = 'social_links'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # GitHub, LinkedIn, Twitter, etc.
    url = Column(String(500), nullable=False)
    icon_name = Column(String(50), nullable=True)  # For icon mapping
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSocialLink(db.Model):
    """Social media links for User (Project Owner)"""
    __tablename__ = 'user_social_links'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # GitHub, LinkedIn, Twitter, etc.
    url = Column(String(500), nullable=False)
    icon_name = Column(String(50), nullable=True)  # For icon mapping
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AboutSection(db.Model):
    """About section configuration"""
    __tablename__ = 'about_section'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, default="My Journey")
    subtitle = Column(String(500), nullable=True)
    skills_title = Column(String(200), nullable=True, default="Core Competencies")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Only one record allowed
    @staticmethod
    def get_config():
        """Get the about section config (singleton)"""
        config = AboutSection.query.first()
        if not config:
            config = AboutSection(
                title="My Journey",
                subtitle="From code to cloud - a timeline of growth and innovation",
                skills_title="Core Competencies"
            )
            db.session.add(config)
            db.session.commit()
        return config

class Timeline(db.Model):
    """Work experience timeline"""
    __tablename__ = 'timeline'
    
    id = Column(Integer, primary_key=True)
    year = Column(String(10), nullable=False)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)  # For icon mapping
    skills = Column(Text, nullable=True)  # JSON string or comma-separated
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Skill(db.Model):
    """Skills with proficiency levels"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    level = Column(Integer, nullable=False)  # 0-100
    color = Column(String(50), nullable=True)  # cyan, purple, pink
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Project(db.Model):
    """Portfolio projects"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string or comma-separated
    icon_name = Column(String(50), nullable=True)
    gradient = Column(String(100), nullable=True)  # CSS gradient classes
    github_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    is_featured = Column(Boolean, default=False)
    status = Column(Boolean, default=True)  # True = active/published, False = inactive/hidden
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlogPost(db.Model):
    """Blog posts"""
    __tablename__ = 'blog_posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=True)  # Full blog content
    image_url = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)  # Blog post URL/slug
    category = Column(String(100), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    read_time = Column(String(50), nullable=True)  # e.g., "12 min read"
    author = Column(String(200), nullable=True)
    is_featured = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContactMessage(db.Model):
    """Contact form submissions"""
    __tablename__ = 'contact_messages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
