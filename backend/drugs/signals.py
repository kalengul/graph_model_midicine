import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from drugs.models import Drug, SideEffect

from ml_pharm_web.utils.thread_locals import get_current_user


logger = logging.getLogger('apilog')


@receiver(post_delete, sender=Drug)
def reindex_drug_delete(sender, instance, **kwargs):
    """Изменение индекс при удалении ЛС."""
    for i, item in enumerate(Drug.objects.order_by('index'),
                             start=1):
        if item.index != i:
            item.index = i
            item.save()


@receiver(post_delete, sender=SideEffect)
def reindex_side_effect_delete(sender, instance, **kwargs):
    """Изменение индекс при удалении ПД."""
    for i, item in enumerate(SideEffect.objects.order_by('index'),
                             start=1):
        if item.index != i:
            item.index = i
            item.save()


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Журналирование создания и изменения."""
    if sender._meta.app_label != 'drugs':
        return

    user = get_current_user()
    username = user.username if user else 'Anonymous'
    action = 'created' if created else 'updated'
    logger.info(f"User {username} {action} {sender.__name__} with id={instance.pk}")


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Журналировния удаления."""
    if sender._meta.app_label != 'drugs':
        return

    user = get_current_user()
    username = user.username if user else 'Anonymous'
    logger.info(f"User {username} deleted {sender.__name__} with id={instance.pk}")
