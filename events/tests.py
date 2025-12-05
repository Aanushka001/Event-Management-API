from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event

import datetime

User = get_user_model()


class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_event_creation(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))

        event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            organizer=self.user,
            location='Test Location',
            start_time=start,
            end_time=end,
            is_public=True
        )
        self.assertEqual(event.title, 'Test Event')


class EventAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_event(self):
        payload = {
            'title': 'API Test Event',
            'description': 'API Test Description',
            'location': 'Test Location',
            'start_time': '2025-12-10T10:00:00Z',
            'end_time': '2025-12-10T12:00:00Z',
            'is_public': True
        }

        response = self.client.post('/api/events/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
