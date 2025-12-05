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
        fields = ['id', 'title', 'description', 'organizer', 'organizer_name', 
                  'location', 'start_time', 'end_time', 'is_public', 'created_at', 'updated_at']
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
    
    def validate(self, data):
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time")
        return data


class RSVPSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = RSVP
        fields = ['id', 'event', 'event_title', 'user', 'user_name', 'status']
        read_only_fields = ['id', 'event', 'user']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'event', 'event_title', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'event', 'user', 'created_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value