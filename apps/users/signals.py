from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def set_username_from_email(sender, instance, created, **kwargs):
    if created and not instance.username and instance.email:
        instance.username = instance.email.split("@")[0]
        instance.save(update_fields=["username"])
