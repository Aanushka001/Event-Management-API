from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('events/<int:event_id>/rsvp/', 
         RSVPViewSet.as_view({'post': 'create', 'get': 'list'}), 
         name='event-rsvp-list'),
    path('events/<int:event_id>/rsvp/<int:pk>/', 
         RSVPViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy', 'get': 'retrieve'}), 
         name='event-rsvp-detail'),
    path('events/<int:event_id>/reviews/', 
         ReviewViewSet.as_view({'post': 'create', 'get': 'list'}), 
         name='event-review-list'),
    path('', include(router.urls)),
]