from rest_framework import permissions
from .models import Event, RSVP


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsInvitedToPrivateEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        event_id = view.kwargs.get('event_id')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                if event.is_public:
                    return True
                if request.user.is_authenticated:
                    return (request.user == event.organizer or 
                           RSVP.objects.filter(event=event, user=request.user).exists())
                return False
            except Event.DoesNotExist:
                return False
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user