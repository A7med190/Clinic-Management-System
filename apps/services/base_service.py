import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from django.db import models

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=models.Model)


class BaseService(ABC, Generic[T]):
    model: type[T]

    def __init__(self):
        if not hasattr(self, "model"):
            raise ValueError(f"{self.__class__.__name__} must define a model attribute")

    def get_queryset(self) -> models.QuerySet[T]:
        return self.model.objects.all()

    def get(self, pk: int) -> T | None:
        try:
            return self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            logger.warning(f"{self.model.__name__} with pk={pk} not found")
            return None

    def list(self) -> models.QuerySet[T]:
        return self.get_queryset()

    def filter(self, **kwargs) -> models.QuerySet[T]:
        return self.get_queryset().filter(**kwargs)

    @abstractmethod
    def create(self, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, instance: T, **kwargs) -> T:
        raise NotImplementedError

    def delete(self, instance: T) -> bool:
        instance.delete()
        return True

    def save(self, instance: T) -> T:
        instance.save()
        return instance


class TransactionalService(BaseService[T]):
    def execute_in_transaction(self, func: callable, *args, **kwargs) -> Any:
        from django.db import transaction

        with transaction.atomic():
            return func(*args, **kwargs)

    def create(self, **kwargs) -> T:
        with transaction.atomic():
            return super().create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        with transaction.atomic():
            return super().update(instance, **kwargs)
