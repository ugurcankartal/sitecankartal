from django.contrib import admin
from django.urls import include, path

from api.views.admin import admin_panel
from api.views.uploads import serve_profile_image

urlpatterns = [
    path('api/v1/', include('api.urls')),
    path('admin/', admin_panel, name='admin-panel'),
    path('admin', admin_panel, name='admin-panel-no-slash'),
    path(
        'static/uploads/profiles/<str:filename>',
        serve_profile_image,
        name='profile-image',
    ),
]
