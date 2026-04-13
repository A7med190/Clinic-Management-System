import pytest
from django.test import TestCase

from apps.services.base_service import BaseService


class TestBaseService(TestCase):
    def test_base_service_requires_model(self):
        with self.assertRaises(ValueError):
            BaseService()

    def test_base_service_model_attribute(self):
        from apps.users.models import User

        class UserService(BaseService):
            model = User

        service = UserService()
        self.assertEqual(service.model, User)

    def test_list_returns_queryset(self):
        from apps.users.models import User

        class UserService(BaseService):
            model = User

        service = UserService()
        queryset = service.list()
        self.assertTrue(hasattr(queryset, "all"))
