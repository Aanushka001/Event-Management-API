from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class EventAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

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

        rsvp_payload = {'status': 'Going'}
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
        self.assertTrue(any('API' in e['title'] for e in search_response.data))
