from django.test import TestCase
from django.urls import reverse


class TestLoginTestCase(TestCase):

    def test_login(self):
        response = self.client.get(reverse('supportSystem:login'))
        self.assertTemplateUsed(response, 'supportSystem/login.html')

    def test_login_redirect(self):
        response = self.client.post(reverse('supportSystem:signin'))
        self.assertContains(response, 'Pasirinkite paskyrą')