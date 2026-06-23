import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import (
    AboutSection,
    BlogPost,
    ContactMessage,
    PortfolioUser,
    Profile,
    Project,
    Skill,
    SocialLink,
    Timeline,
    UserSocialLink,
)
from api.utils import (
    allowed_file,
    join_csv,
    login_required,
    normalize_image_url,
    serialize_blog_post,
    serialize_project,
    serialize_skill,
    serialize_social_link,
    serialize_timeline,
    split_csv,
)

logger = logging.getLogger(__name__)


def _csrf_exempt_api_view(methods):
    def decorator(func):
        wrapped = csrf_exempt(api_view(methods)(func))
        return wrapped

    return decorator


# ==================== PROFILE ====================

def get_profile(request):
    profile = Profile.objects.first()
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    social_links = SocialLink.objects.filter(profile_id=profile.id).order_by('display_order')

    return Response({
        'id': profile.id,
        'name': profile.name,
        'title': profile.title,
        'description': profile.description,
        'profile_image_url': normalize_image_url(profile.profile_image_url),
        'email': profile.email,
        'phone': profile.phone,
        'location': profile.location,
        'social_links': [serialize_social_link(link) for link in social_links],
    })


def update_profile(request):
    data = request.data
    profile = Profile.objects.first()
    if not profile:
        profile = Profile(
            name=data.get('name', ''),
            title=data.get('title', ''),
        )

    profile.name = data.get('name', profile.name)
    profile.title = data.get('title', profile.title)
    profile.description = data.get('description', profile.description)
    profile.profile_image_url = data.get('profile_image_url', profile.profile_image_url)
    profile.email = data.get('email', profile.email)
    profile.phone = data.get('phone', profile.phone)
    profile.location = data.get('location', profile.location)
    profile.save()

    return Response({'message': 'Profile updated successfully', 'id': profile.id})


# ==================== ABOUT ====================

def get_about_section(request):
    config = AboutSection.objects.first()
    if not config:
        config = AboutSection.objects.create(
            title='My Journey',
            subtitle='From code to cloud - a timeline of growth and innovation',
            skills_title='Core Competencies',
        )

    return Response({
        'id': config.id,
        'title': config.title,
        'subtitle': config.subtitle,
        'skills_title': config.skills_title,
    })


@login_required
def update_about_section(request):
    config = AboutSection.objects.first()
    if not config:
        config = AboutSection(
            title='My Journey',
            subtitle='From code to cloud - a timeline of growth and innovation',
            skills_title='Core Competencies',
        )

    data = request.data
    config.title = data.get('title', config.title)
    config.subtitle = data.get('subtitle', config.subtitle)
    config.skills_title = data.get('skills_title', config.skills_title)
    config.save()

    return Response({'message': 'About section updated'})


# ==================== TIMELINE ====================

def get_timeline(request):
    timeline = Timeline.objects.all().order_by('display_order', '-year')
    return Response([serialize_timeline(item) for item in timeline])


@login_required
def create_timeline(request):
    data = request.data
    timeline = Timeline.objects.create(
        year=data.get('year'),
        title=data.get('title'),
        company=data.get('company'),
        description=data.get('description'),
        icon_name=data.get('icon_name'),
        skills=join_csv(data.get('skills', [])),
        display_order=data.get('display_order', 0),
    )
    return Response(
        {'message': 'Timeline entry created', 'id': timeline.id},
        status=status.HTTP_201_CREATED,
    )


def get_timeline_entry(request, id):
    timeline = get_object_or_404(Timeline, pk=id)
    return Response(serialize_timeline(timeline))


@login_required
def update_timeline(request, id):
    timeline = get_object_or_404(Timeline, pk=id)
    data = request.data

    timeline.year = data.get('year', timeline.year)
    timeline.title = data.get('title', timeline.title)
    timeline.company = data.get('company', timeline.company)
    timeline.description = data.get('description', timeline.description)
    timeline.icon_name = data.get('icon_name', timeline.icon_name)
    timeline.skills = join_csv(data.get('skills', split_csv(timeline.skills)))
    timeline.display_order = data.get('display_order', timeline.display_order)
    timeline.save()

    return Response({'message': 'Timeline entry updated'})


@login_required
def delete_timeline(request, id):
    timeline = get_object_or_404(Timeline, pk=id)
    timeline.delete()
    return Response({'message': 'Timeline entry deleted'})


# ==================== SKILLS ====================

def get_skills(request):
    skills = Skill.objects.all().order_by('display_order')
    return Response([serialize_skill(skill) for skill in skills])


@login_required
def create_skill(request):
    data = request.data
    skill = Skill.objects.create(
        name=data.get('name'),
        level=data.get('level', 0),
        color=data.get('color'),
        display_order=data.get('display_order', 0),
    )
    return Response(
        {'message': 'Skill created', 'id': skill.id},
        status=status.HTTP_201_CREATED,
    )


def get_skill(request, id):
    skill = get_object_or_404(Skill, pk=id)
    return Response(serialize_skill(skill))


@login_required
def update_skill(request, id):
    skill = get_object_or_404(Skill, pk=id)
    data = request.data

    skill.name = data.get('name', skill.name)
    skill.level = data.get('level', skill.level)
    skill.color = data.get('color', skill.color)
    skill.display_order = data.get('display_order', skill.display_order)
    skill.save()

    return Response({'message': 'Skill updated'})


@login_required
def delete_skill(request, id):
    skill = get_object_or_404(Skill, pk=id)
    skill.delete()
    return Response({'message': 'Skill deleted'})


# ==================== PROJECTS ====================

def get_projects(request):
    status_filter = request.query_params.get('status')
    queryset = Project.objects.all()

    if status_filter is None:
        queryset = queryset.filter(status=True)
    elif status_filter.lower() != 'all':
        queryset = queryset.filter(status=(status_filter.lower() == 'true'))

    projects = queryset.order_by('display_order', '-created_at')
    return Response([serialize_project(project) for project in projects])


def get_project(request, id):
    project = get_object_or_404(Project, pk=id)
    return Response(serialize_project(project))


@login_required
def create_project(request):
    data = request.data
    project = Project.objects.create(
        title=data.get('title'),
        description=data.get('description'),
        image_url=data.get('image_url'),
        tags=join_csv(data.get('tags', [])),
        icon_name=data.get('icon_name'),
        gradient=data.get('gradient'),
        github_url=data.get('github_url'),
        demo_url=data.get('demo_url'),
        is_featured=data.get('is_featured', False),
        status=data.get('status', True),
        display_order=data.get('display_order', 0),
    )
    return Response(
        {'message': 'Project created', 'id': project.id},
        status=status.HTTP_201_CREATED,
    )


@login_required
def update_project(request, id):
    project = get_object_or_404(Project, pk=id)
    data = request.data

    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.image_url = data.get('image_url', project.image_url)
    project.tags = join_csv(data.get('tags', split_csv(project.tags)))
    project.icon_name = data.get('icon_name', project.icon_name)
    project.gradient = data.get('gradient', project.gradient)
    project.github_url = data.get('github_url', project.github_url)
    project.demo_url = data.get('demo_url', project.demo_url)
    project.is_featured = data.get('is_featured', project.is_featured)
    if 'status' in data:
        project.status = data.get('status')
    project.display_order = data.get('display_order', project.display_order)
    project.save()

    return Response({'message': 'Project updated'})


@login_required
def delete_project(request, id):
    project = get_object_or_404(Project, pk=id)
    project.delete()
    return Response({'message': 'Project deleted'})


# ==================== BLOG ====================

def get_blog_posts(request):
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', settings.POSTS_PER_PAGE))
    featured_only = request.query_params.get('featured', '').lower() in ('true', '1')
    all_posts = request.query_params.get('all', '').lower() in ('true', '1')

    per_page = min(per_page, 100)

    queryset = BlogPost.objects.all()
    if not all_posts:
        queryset = queryset.filter(is_published=True)
    if featured_only:
        queryset = queryset.filter(is_featured=True)

    queryset = queryset.order_by('display_order', '-date')
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)

    return Response({
        'posts': [serialize_blog_post(post) for post in page_obj.object_list],
        'total': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page,
    })


def get_blog_post(request, id):
    post = get_object_or_404(BlogPost, pk=id)
    return Response(serialize_blog_post(post))


def _parse_datetime(value):
    if not value:
        return timezone.now()
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed)
    return parsed


@login_required
def create_blog_post(request):
    data = request.data
    post = BlogPost.objects.create(
        title=data.get('title'),
        excerpt=data.get('excerpt'),
        content=data.get('content'),
        image_url=data.get('image_url'),
        url=data.get('url'),
        category=data.get('category'),
        date=_parse_datetime(data.get('date')),
        read_time=data.get('read_time'),
        author=data.get('author'),
        is_featured=data.get('is_featured', False),
        is_published=data.get('is_published', True),
        display_order=data.get('display_order', 0),
    )
    return Response(
        {'message': 'Blog post created', 'id': post.id},
        status=status.HTTP_201_CREATED,
    )


@login_required
def update_blog_post(request, id):
    post = get_object_or_404(BlogPost, pk=id)
    data = request.data

    post.title = data.get('title', post.title)
    post.excerpt = data.get('excerpt', post.excerpt)
    post.content = data.get('content', post.content)
    post.image_url = data.get('image_url', post.image_url)
    post.url = data.get('url', post.url)
    post.category = data.get('category', post.category)
    if data.get('date'):
        post.date = _parse_datetime(data.get('date'))
    post.read_time = data.get('read_time', post.read_time)
    post.author = data.get('author', post.author)
    post.is_featured = data.get('is_featured', post.is_featured)
    post.is_published = data.get('is_published', post.is_published)
    post.display_order = data.get('display_order', post.display_order)
    post.save()

    return Response({'message': 'Blog post updated'})


@login_required
def delete_blog_post(request, id):
    post = get_object_or_404(BlogPost, pk=id)
    post.delete()
    return Response({'message': 'Blog post deleted'})


# ==================== CONTACT ====================

def submit_contact(request):
    data = request.data
    message = ContactMessage.objects.create(
        name=data.get('name'),
        email=data.get('email'),
        subject=data.get('subject'),
        message=data.get('message'),
    )
    return Response(
        {'message': 'Contact message submitted successfully', 'id': message.id},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@login_required
def get_contact_messages(request):
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 20))

    queryset = ContactMessage.objects.all().order_by('-created_at')
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)

    return Response({
        'messages': [{
            'id': msg.id,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message,
            'is_read': msg.is_read,
            'created_at': msg.created_at.isoformat() if msg.created_at else None,
        } for msg in page_obj.object_list],
        'total': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page,
    })


# ==================== AUTH ====================

@_csrf_exempt_api_view(['POST'])
def login(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = PortfolioUser.objects.filter(username=username).first()

    if user and user.check_password(password):
        request.session.cycle_key()
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
            },
        })

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@_csrf_exempt_api_view(['POST'])
def logout(request):
    request.session.flush()
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
def check_auth(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = PortfolioUser.objects.filter(pk=user_id).first()
        if user:
            return Response({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                },
            })
    return Response({'authenticated': False})


# ==================== USER ====================

@api_view(['GET'])
def get_public_user_info(request):
    user = PortfolioUser.objects.first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    social_links = UserSocialLink.objects.filter(user_id=user.id).order_by('display_order')

    profile_image_url = None
    if user.profile_image_url:
        if user.profile_image_url.startswith('/static/'):
            profile_image_url = user.profile_image_url
        else:
            profile_image_url = f'/static/uploads/profiles/{user.profile_image_url}'

    return Response({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'bio': user.bio,
        'location': user.location,
        'profile_image_url': normalize_image_url(profile_image_url),
        'social_links': [serialize_social_link(link) for link in social_links],
    })


@login_required
def get_user_info(request):
    user = get_object_or_404(PortfolioUser, pk=request.session['user_id'])
    return Response({
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'bio': user.bio,
        'location': user.location,
        'profile_image_url': user.profile_image_url,
    })


@login_required
def update_user_info(request):
    user = get_object_or_404(PortfolioUser, pk=request.session['user_id'])
    data = request.data

    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.bio = data.get('bio', user.bio)
    user.location = data.get('location', user.location)
    user.profile_image_url = data.get('profile_image_url', user.profile_image_url)
    user.save()

    return Response({'message': 'User information updated'})


@_csrf_exempt_api_view(['PUT'])
@login_required
def change_password(request):
    user = get_object_or_404(PortfolioUser, pk=request.session['user_id'])
    data = request.data
    new_password = data.get('password')

    if not new_password or len(new_password) < 6:
        return Response(
            {'error': 'Şifre en az 6 karakter olmalıdır'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Şifre başarıyla güncellendi'})


# ==================== USER SOCIAL LINKS ====================

def get_user_social_links(request):
    user = PortfolioUser.objects.first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    links = UserSocialLink.objects.filter(user_id=user.id).order_by('display_order')
    return Response([serialize_social_link(link) for link in links])


@login_required
def create_user_social_link(request):
    user = PortfolioUser.objects.first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    link = UserSocialLink.objects.create(
        user_id=user.id,
        platform=data.get('platform'),
        url=data.get('url'),
        icon_name=data.get('icon_name'),
        display_order=data.get('display_order', 0),
    )
    return Response(
        {'message': 'Social link created', 'id': link.id},
        status=status.HTTP_201_CREATED,
    )


def get_user_social_link(request, id):
    link = get_object_or_404(UserSocialLink, pk=id)
    return Response(serialize_social_link(link))


@login_required
def update_user_social_link(request, id):
    link = get_object_or_404(UserSocialLink, pk=id)
    data = request.data

    link.platform = data.get('platform', link.platform)
    link.url = data.get('url', link.url)
    link.icon_name = data.get('icon_name', link.icon_name)
    link.display_order = data.get('display_order', link.display_order)
    link.save()

    return Response({'message': 'Social link updated'})


@login_required
def delete_user_social_link(request, id):
    link = get_object_or_404(UserSocialLink, pk=id)
    link.delete()
    return Response({'message': 'Social link deleted'})


# ==================== UPLOADS ====================

@_csrf_exempt_api_view(['POST'])
@login_required
def upload_profile_image(request):
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file part'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        if not file.name:
            return Response({'error': 'No selected file'}, status=status.HTTP_400_BAD_REQUEST)

        if not allowed_file(file.name):
            return Response({'error': 'File type not allowed'}, status=status.HTTP_400_BAD_REQUEST)

        user = PortfolioUser.objects.first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.profile_image_url:
            old_filename = user.profile_image_url
            if '/' in old_filename:
                old_filename = old_filename.split('/')[-1]

            old_file_path = Path(settings.UPLOAD_FOLDER) / 'profiles' / old_filename
            if old_file_path.exists():
                try:
                    old_file_path.unlink()
                except OSError as exc:
                    logger.warning('Could not delete old profile image: %s', exc)

        profiles_dir = Path(settings.UPLOAD_FOLDER) / 'profiles'
        profiles_dir.mkdir(parents=True, exist_ok=True)

        from django.utils.text import get_valid_filename

        filename = get_valid_filename(file.name)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_filename = f'{timestamp}_{filename}'
        file_path = profiles_dir / unique_filename

        try:
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except Exception as exc:
            logger.error('Error saving file: %s', exc)
            return Response(
                {'error': f'Failed to save file: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user.profile_image_url = unique_filename
        try:
            user.save()
        except Exception as exc:
            logger.error('Error committing to database: %s', exc)
            if file_path.exists():
                try:
                    file_path.unlink()
                except OSError:
                    pass
            return Response(
                {'error': f'Failed to update database: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({
            'message': 'Profile image uploaded successfully',
            'url': f'/static/uploads/profiles/{unique_filename}',
        })

    except Exception as exc:
        logger.error('Unexpected error in upload_profile_image: %s', exc, exc_info=True)
        return Response(
            {'error': f'Internal server error: {exc}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@_csrf_exempt_api_view(['DELETE'])
@login_required
def delete_profile_image(request):
    user = PortfolioUser.objects.first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if user.profile_image_url:
        file_path = Path(settings.UPLOAD_FOLDER) / 'profiles' / user.profile_image_url
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass

        user.profile_image_url = None
        user.save()
        return Response({'message': 'Profile image deleted successfully'})

    return Response({'message': 'No profile image to delete'})


# ==================== COMBINED ROUTE HANDLERS ====================

@csrf_exempt
@api_view(['GET', 'POST', 'PUT'])
def profile(request):
    if request.method == 'GET':
        return get_profile(request)
    return update_profile(request)


@csrf_exempt
@api_view(['GET', 'PUT'])
def about(request):
    if request.method == 'GET':
        return get_about_section(request)
    return update_about_section(request)


@csrf_exempt
@api_view(['GET', 'POST'])
def timeline_list(request):
    if request.method == 'GET':
        return get_timeline(request)
    return create_timeline(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def timeline_detail(request, id):
    if request.method == 'GET':
        return get_timeline_entry(request, id)
    if request.method == 'PUT':
        return update_timeline(request, id)
    return delete_timeline(request, id)


@csrf_exempt
@api_view(['GET', 'POST'])
def skills_list(request):
    if request.method == 'GET':
        return get_skills(request)
    return create_skill(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def skill_detail(request, id):
    if request.method == 'GET':
        return get_skill(request, id)
    if request.method == 'PUT':
        return update_skill(request, id)
    return delete_skill(request, id)


@csrf_exempt
@api_view(['GET', 'POST'])
def projects_list(request):
    if request.method == 'GET':
        return get_projects(request)
    return create_project(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def project_detail(request, id):
    if request.method == 'GET':
        return get_project(request, id)
    if request.method == 'PUT':
        return update_project(request, id)
    return delete_project(request, id)


@csrf_exempt
@api_view(['GET', 'POST'])
def blog_list(request):
    if request.method == 'GET':
        return get_blog_posts(request)
    return create_blog_post(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def blog_detail(request, id):
    if request.method == 'GET':
        return get_blog_post(request, id)
    if request.method == 'PUT':
        return update_blog_post(request, id)
    return delete_blog_post(request, id)


@csrf_exempt
@api_view(['POST'])
def contact(request):
    return submit_contact(request)


@csrf_exempt
@api_view(['GET', 'PUT'])
def admin_user(request):
    if request.method == 'GET':
        return get_user_info(request)
    return update_user_info(request)


@csrf_exempt
@api_view(['GET', 'POST'])
def user_social_links(request):
    if request.method == 'GET':
        return get_user_social_links(request)
    return create_user_social_link(request)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def user_social_link_detail(request, id):
    if request.method == 'GET':
        return get_user_social_link(request, id)
    if request.method == 'PUT':
        return update_user_social_link(request, id)
    return delete_user_social_link(request, id)

