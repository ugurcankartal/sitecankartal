from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Personal Portfolio API',
        'version': '1.0.0',
        'endpoints': {
            'profile': '/api/v1/profile',
            'timeline': '/api/v1/timeline',
            'skills': '/api/v1/skills',
            'projects': '/api/v1/projects',
            'blog': '/api/v1/blog',
            'contact': '/api/v1/contact',
            'health': '/api/v1/health',
        },
        'documentation': 'See README.md for API documentation',
    })


@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'message': 'API is running'})
