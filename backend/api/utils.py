from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from rest_framework.response import Response
from rest_framework import status


def normalize_image_url(url):
    if not url:
        return None

    if url.startswith('/'):
        return url

    if 'localhost:5000' in url or '127.0.0.1:5000' in url:
        try:
            parsed = urlparse(url)
            return parsed.path if parsed.path else url
        except Exception:
            if '/static/' in url:
                return '/static/' + url.split('/static/')[1]
            return url

    if 'localhost:8000' in url or '127.0.0.1:8000' in url:
        try:
            parsed = urlparse(url)
            return parsed.path if parsed.path else url
        except Exception:
            if '/static/' in url:
                return '/static/' + url.split('/static/')[1]
            return url

    if url.startswith('http://') or url.startswith('https://'):
        return url

    return f'/{url}' if not url.startswith('/') else url


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
    )


def split_csv(value):
    if not value:
        return []
    return value.split(',')


def join_csv(value):
    if isinstance(value, list):
        return ','.join(value)
    return value


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return view_func(request, *args, **kwargs)

    return wrapper


def serialize_social_link(link):
    return {
        'id': link.id,
        'platform': link.platform,
        'url': link.url,
        'icon_name': link.icon_name,
        'display_order': link.display_order,
    }


def serialize_timeline(item):
    return {
        'id': item.id,
        'year': item.year,
        'title': item.title,
        'company': item.company,
        'description': item.description,
        'icon_name': item.icon_name,
        'skills': split_csv(item.skills),
        'display_order': item.display_order,
    }


def serialize_skill(skill):
    return {
        'id': skill.id,
        'name': skill.name,
        'level': skill.level,
        'color': skill.color,
        'display_order': skill.display_order,
    }


def serialize_project(project):
    return {
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'image_url': normalize_image_url(project.image_url),
        'tags': split_csv(project.tags),
        'icon_name': project.icon_name,
        'gradient': project.gradient,
        'github_url': project.github_url,
        'demo_url': project.demo_url,
        'is_featured': project.is_featured,
        'status': project.status,
        'display_order': project.display_order,
    }


def serialize_blog_post(post):
    return {
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
        'is_published': post.is_published,
    }
