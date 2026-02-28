from django.test import TestCase
from rest_framework.test import APIClient
from .models import School, User

class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration(self):
        response = self.client.post('/api/v1/auth/register/', {
            "school_name": "Lagos Prep",
            "school_slug": "lagos-prep",
            "school_email": "info@lagosprep.com",
            "owner_username": "owner1",
            "owner_password": "password123",
            "owner_email": "owner@lagosprep.com"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(School.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().role, 'owner')

    def test_login_and_access(self):
        # Register first
        self.client.post('/api/v1/auth/register/', {
            "school_name": "School B",
            "school_slug": "school-b",
            "school_email": "info@schoolb.com",
            "owner_username": "owner2",
            "owner_password": "password123",
            "owner_email": "owner@schoolb.com"
        })

        # Login
        response = self.client.post('/api/v1/token/', {
            "username": "owner2",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        token = response.data['access']

        # Access students list
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/students/')
        self.assertEqual(response.status_code, 200)
