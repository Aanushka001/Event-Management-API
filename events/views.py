from rest_framework import viewsets, status, serializers, permissions, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedToPrivateEvent, IsOwnerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOrganizerOrReadOnly,
        IsInvitedToPrivateEvent
    ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'is_public']
    search_fields = ['title', 'location', 'organizer__username']
    ordering_fields = ['start_time', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Event.objects.filter(
                Q(is_public=True) | 
                Q(organizer=user) | 
                Q(rsvps__user=user)
            ).distinct()
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class RSVPViewSet(viewsets.ModelViewSet):
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated, IsInvitedToPrivateEvent, IsOwnerOrReadOnly]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return RSVP.objects.filter(event_id=event_id)
        return RSVP.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        
        if not event_id:
            raise serializers.ValidationError({"event": "Event ID is required."})
        
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError({"event": "Event not found."})
        
        if RSVP.objects.filter(user=self.request.user, event=event).exists():
            raise serializers.ValidationError(
                {"detail": "You have already RSVP'd to this event."}
            )
        
        serializer.save(user=self.request.user, event=event)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if 'status' not in request.data:
            return Response(
                {"detail": "Only status field can be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            instance, 
            data={'status': request.data['status']}, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        if event_id:
            return Review.objects.filter(event_id=event_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        if not event_id:
            raise serializers.ValidationError({"event": "Event ID is required."})
        
        if Review.objects.filter(user=self.request.user, event_id=event_id).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this event."}
            )
        
        serializer.save(user=self.request.user, event_id=event_id)