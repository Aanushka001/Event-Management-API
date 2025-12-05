from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Event, RSVP, Review
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
        self.assertEqual(event.organizer, self.user)
        self.assertTrue(event.is_public)

    def test_event_str_method(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))

        event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            organizer=self.user,
            location='Test Location',
            start_time=start,
            end_time=end
        )
        self.assertEqual(str(event), 'Test Event')


class RSVPModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            organizer=self.user,
            location='Test Location',
            start_time=start,
            end_time=end
        )

    def test_rsvp_creation(self):
        rsvp = RSVP.objects.create(
            event=self.event,
            user=self.user,
            status='going'
        )
        self.assertEqual(rsvp.status, 'going')
        self.assertEqual(rsvp.event, self.event)


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            organizer=self.user,
            location='Test Location',
            start_time=start,
            end_time=end
        )

    def test_review_creation(self):
        review = Review.objects.create(
            event=self.event,
            user=self.user,
            rating=5,
            comment='Great event!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great event!')


class BaseAPITest(APITestCase):
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class EventAPITest(BaseAPITest):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass')
        self.authenticate(self.user)

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
        self.assertEqual(response.data['title'], 'API Test Event')

    def test_event_flow(self):
        payload = {
            'title': 'API Test Event',
            'description': 'Automatically created test event',
            'location': 'Earth',
            'start_time': '2025-12-20T18:00:00Z',
            'end_time': '2025-12-20T20:00:00Z',
            'is_public': True
        }
        event_response = self.client.post('/api/events/', payload, format='json')
        self.assertEqual(event_response.status_code, status.HTTP_201_CREATED)
        event_id = event_response.data['id']

        event_detail_response = self.client.get(f'/api/events/{event_id}/')
        self.assertEqual(event_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(event_detail_response.data['title'], 'API Test Event')

        rsvp_payload = {'status': 'going'}
        rsvp_response = self.client.post(f'/api/events/{event_id}/rsvp/', rsvp_payload, format='json')
        self.assertEqual(rsvp_response.status_code, status.HTTP_201_CREATED)

        review_payload = {'rating': 5, 'comment': 'Excellent event!'}
        review_response = self.client.post(f'/api/events/{event_id}/reviews/', review_payload, format='json')
        self.assertEqual(review_response.status_code, status.HTTP_201_CREATED)

        rsvp_list_response = self.client.get(f'/api/events/{event_id}/rsvp/')
        self.assertEqual(rsvp_list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(rsvp_list_response.data), 1)

        review_list_response = self.client.get(f'/api/events/{event_id}/reviews/')
        self.assertEqual(review_list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(review_list_response.data), 1)

        search_response = self.client.get('/api/events/?search=api')
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        events_list = search_response.data.get('results', search_response.data)
        self.assertTrue(any('API' in e['title'] for e in events_list))

    def test_list_events(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        Event.objects.create(
            title='Public Event',
            description='Description',
            organizer=self.user,
            location='Location',
            start_time=start,
            end_time=end,
            is_public=True
        )
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_update_event_as_organizer(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        event = Event.objects.create(
            title='Original Title',
            description='Description',
            organizer=self.user,
            location='Location',
            start_time=start,
            end_time=end
        )
        payload = {
            'title': 'Updated Title',
            'description': 'Description',
            'location': 'Location',
            'start_time': '2025-12-10T10:00:00Z',
            'end_time': '2025-12-10T12:00:00Z'
        }
        response = self.client.put(f'/api/events/{event.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_delete_event_as_organizer(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        event = Event.objects.create(
            title='Event to Delete',
            description='Description',
            organizer=self.user,
            location='Location',
            start_time=start,
            end_time=end
        )
        response = self.client.delete(f'/api/events/{event.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_update_others_event(self):
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        event = Event.objects.create(
            title='Other Event',
            description='Description',
            organizer=self.other_user,
            location='Location',
            start_time=start,
            end_time=end
        )
        payload = {
            'title': 'Hacked Title',
            'description': 'Description',
            'location': 'Location',
            'start_time': '2025-12-10T10:00:00Z',
            'end_time': '2025-12-10T12:00:00Z'
        }
        response = self.client.put(f'/api/events/{event.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RSVPAPITest(BaseAPITest):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.authenticate(self.user)
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        self.event = Event.objects.create(
            title='Test Event',
            description='Description',
            organizer=self.user,
            location='Location',
            start_time=start,
            end_time=end,
            is_public=True
        )

    def test_create_rsvp(self):
        payload = {
            'status': 'going'
        }
        response = self.client.post(f'/api/events/{self.event.id}/rsvp/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'going')

    def test_list_rsvps(self):
        RSVP.objects.create(event=self.event, user=self.user, status='going')
        response = self.client.get(f'/api/events/{self.event.id}/rsvp/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_rsvp(self):
        rsvp = RSVP.objects.create(event=self.event, user=self.user, status='maybe')
        payload = {'status': 'going'}
        response = self.client.patch(f'/api/events/{self.event.id}/rsvp/{rsvp.id}/', payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'going')


class ReviewAPITest(BaseAPITest):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.authenticate(self.user)
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        self.event = Event.objects.create(
            title='Test Event',
            description='Description',
            organizer=self.user,
            location='Location',
            start_time=start,
            end_time=end,
            is_public=True
        )

    def test_create_review(self):
        payload = {
            'rating': 5,
            'comment': 'Excellent event!'
        }
        response = self.client.post(f'/api/events/{self.event.id}/reviews/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

    def test_list_reviews(self):
        Review.objects.create(event=self.event, user=self.user, rating=4, comment='Good')
        response = self.client.get(f'/api/events/{self.event.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_invalid_rating(self):
        payload = {
            'rating': 6,
            'comment': 'Invalid rating'
        }
        response = self.client.post(f'/api/events/{self.event.id}/reviews/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PermissionTest(BaseAPITest):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        start = timezone.make_aware(datetime.datetime(2025, 12, 10, 10, 0, 0))
        end = timezone.make_aware(datetime.datetime(2025, 12, 10, 12, 0, 0))
        self.private_event = Event.objects.create(
            title='Private Event',
            description='Description',
            organizer=self.user1,
            location='Location',
            start_time=start,
            end_time=end,
            is_public=False
        )

    def test_private_event_not_visible_to_non_invited_user(self):
        self.authenticate(self.user2)
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event_ids = [event['id'] for event in response.data.get('results', [])]
        self.assertNotIn(self.private_event.id, event_ids)

    def test_private_event_visible_to_organizer(self):
        self.authenticate(self.user1)
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event_ids = [event['id'] for event in response.data.get('results', [])]
        self.assertIn(self.private_event.id, event_ids)

    def test_private_event_visible_to_invited_user(self):
        RSVP.objects.create(event=self.private_event, user=self.user2, status='going')
        self.authenticate(self.user2)
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event_ids = [event['id'] for event in response.data.get('results', [])]
        self.assertIn(self.private_event.id, event_ids)