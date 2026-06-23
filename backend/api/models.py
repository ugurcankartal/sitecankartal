from django.db import models
from werkzeug.security import check_password_hash, generate_password_hash


class PortfolioUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    profile_image_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __str__(self):
        return self.username


class Profile(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    profile_image_url = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'


class SocialLink(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='social_links',
        db_column='profile_id',
    )
    platform = models.CharField(max_length=50)
    url = models.CharField(max_length=500)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_links'


class UserSocialLink(models.Model):
    user = models.ForeignKey(
        PortfolioUser,
        on_delete=models.CASCADE,
        related_name='social_links',
        db_column='user_id',
    )
    platform = models.CharField(max_length=50)
    url = models.CharField(max_length=500)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_social_links'


class AboutSection(models.Model):
    title = models.CharField(max_length=200, default='My Journey')
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    skills_title = models.CharField(max_length=200, blank=True, null=True, default='Core Competencies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'about_section'


class Timeline(models.Model):
    year = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timeline'
        ordering = ['display_order', '-year']


class Skill(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()
    color = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'skills'
        ordering = ['display_order']


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.CharField(max_length=500, blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    gradient = models.CharField(max_length=100, blank=True, null=True)
    github_url = models.CharField(max_length=500, blank=True, null=True)
    demo_url = models.CharField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['display_order', '-created_at']


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    content = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()
    read_time = models.CharField(max_length=50, blank=True, null=True)
    author = models.CharField(max_length=200, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_posts'
        ordering = ['display_order', '-date']


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
