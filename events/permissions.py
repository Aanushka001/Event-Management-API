from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.organizer == request.user


class IsEventOrganizerOrReadOnly(permissions.BasePermission):
    """
    Permission for event-related nested resources (RSVP, Review)
    Organizers can do anything, others can only read
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        
        return False


class CanAccessEvent(permissions.BasePermission):
    """
    Permission to restrict access to private events.
    Only the organizer and invited users can access private events.
    """

    def has_object_permission(self, request, view, obj):
        # If event is public, allow access
        if obj.is_public:
            return True

        if not request.user.is_authenticated:
            return False

        if obj.organizer == request.user:
            return True

        if request.user in obj.invited_users.all():
            return True

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class CanRSVPToEvent(permissions.BasePermission):
    """
    Permission to check if user can RSVP to an event.
    Users can RSVP to public events or private events they're invited to.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        event_id = view.kwargs.get('event_id')
        if not event_id:
            return False

        from .models import Event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return False

        # Check if event is public or user is invited
        if event.is_public:
            return True

        if request.user in event.invited_users.all():
            return True

        if event.organizer == request.user:
            return True

        return False


class CanReviewEvent(permissions.BasePermission):
    """
    Permission to check if user can review an event.
    Users can only review events they attended (RSVP status = 'going').
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == 'GET':
            return True

        event_id = view.kwargs.get('event_id')
        if not event_id:
            return False

        from .models import Event, RSVP
        from django.utils import timezone

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return False

        if event.end_time > timezone.now():
            return False

        has_rsvp = RSVP.objects.filter(
            event=event,
            user=request.user,
            status='going'
        ).exists()

        return has_rsvp