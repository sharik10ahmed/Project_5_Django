from django.db import migrations


def backfill_confirmed_status(apps, schema_editor):
    Order = apps.get_model('PickUp', 'Order')
    Order.objects.filter(status='Pending').update(status='Confirmed')


class Migration(migrations.Migration):

    dependencies = [
        ('PickUp', '0016_order_tracking_number'),
    ]

    operations = [
        migrations.RunPython(backfill_confirmed_status, migrations.RunPython.noop),
    ]
