import pytest
from django.test import TestCase


@pytest.mark.django_db
class TestHealthCheck(TestCase):
    def test_health_check_endpoint(self):
        from django.test import Client
        client = Client()
        response = client.get("/health/")
        self.assertIn(response.status_code, [200, 503])
