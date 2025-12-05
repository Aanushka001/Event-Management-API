from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Event, RSVP, Review


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'username', 'full_name', 'bio', 'location', 'profile_picture']
        read_only_fields = ['id', 'user']


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer', 'organizer_name',
            'location', 'start_time', 'end_time', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

    def validate(self, data):
        start_time = data.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = data.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class RSVPSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'event_title', 'user', 'user_name', 'status']
        read_only_fields = ['id', 'user', 'event']

    def validate_status(self, value):
        STATUS_CHOICES = dict(RSVP.STATUS_CHOICES)
        
        if value in STATUS_CHOICES:
            return value
            
        value_lower = value.lower()
        reverse_choices = {v.lower(): k for k, v in STATUS_CHOICES.items()}
        
        if value_lower in reverse_choices:
            return reverse_choices[value_lower]
            
        raise serializers.ValidationError(
            f"Status must be one of: {', '.join(STATUS_CHOICES.values())}"
        )


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'event', 'event_title', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'event', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value