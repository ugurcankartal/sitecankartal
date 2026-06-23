from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def serve_profile_image(request, filename):
    profiles_dir = Path(settings.UPLOAD_FOLDER) / 'profiles'
    file_path = profiles_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise Http404('File not found')

    return FileResponse(open(file_path, 'rb'))
