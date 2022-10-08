from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .loop_manager import q
from .models import Profile

User = get_user_model()


@receiver(post_save, sender='common.Device', dispatch_uid="common.post_save_update_devices")
def post_save_update_devices(sender, instance, created, raw, **kwargs):
    q.put({"updated" if not created else "created": instance.id})


@receiver(post_delete, sender='common.Device', dispatch_uid="common.post_delete_update_devices")
def post_delete_update_devices(sender, instance, **kwargs):
    q.put({"deleted": instance.id})


@receiver(post_save, sender=User, dispatch_uid="common.post_save_create_profile")
def post_save_create_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        profile = Profile(user=user)
        profile.save()
