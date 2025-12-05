from rest_framework import permissions
from .models import Event, RSVP


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsInvitedToPrivateEvent(permissions.BasePermission):
    def has_permission(self, request, view):
        event_id = view.kwargs.get('event_id')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                if not event.is_public and request.user.is_authenticated:
                    if request.user != event.organizer:
                        return RSVP.objects.filter(event=event, user=request.user).exists()
            except Event.DoesNotExist:
                return False
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user