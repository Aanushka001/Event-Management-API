"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def api_root(request):
    return JsonResponse({
        'message': 'Welcome to Event Management API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'events': '/api/events/',
                'token': '/api/token/',
                'token_refresh': '/api/token/refresh/',
            },
            'documentation': {
                'events_list': 'GET /api/events/ - List all events',
                'events_create': 'POST /api/events/ - Create event (auth required)',
                'events_detail': 'GET /api/events/{id}/ - Get event details',
                'events_update': 'PUT/PATCH /api/events/{id}/ - Update event (organizer only)',
                'events_delete': 'DELETE /api/events/{id}/ - Delete event (organizer only)',
                'rsvp_create': 'POST /api/events/{id}/rsvp/ - RSVP to event',
                'rsvp_list': 'GET /api/events/{id}/rsvp/ - List RSVPs',
                'rsvp_update': 'PATCH /api/events/{id}/rsvp/{rsvp_id}/ - Update RSVP',
                'reviews_create': 'POST /api/events/{id}/reviews/ - Add review',
                'reviews_list': 'GET /api/events/{id}/reviews/ - List reviews',
            }
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('events.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)