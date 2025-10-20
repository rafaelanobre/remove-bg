from django.test import Client, TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_returns_200(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)

    def test_health_check_returns_json(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_health_check_status_ok(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.json(), {'status': 'OK'})

class HomePageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'processor/home.html')
