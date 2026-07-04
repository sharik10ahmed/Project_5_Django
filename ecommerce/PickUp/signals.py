from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order
from .email_utils import send_order_status_email


@receiver(pre_save, sender=Order)
def cache_order_status_before_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    instance._previous_status = previous.status


@receiver(post_save, sender=Order)
def send_status_change_email(sender, instance, created, **kwargs):
    if created:
        return
    previous_status = getattr(instance, '_previous_status', None)
    if not previous_status:
        return
    if instance.status == previous_status:
        return
    if instance.status in {'Shipped', 'Delivered', 'Cancelled'}:
        send_order_status_email(instance, instance.status, previous_status=previous_status)
