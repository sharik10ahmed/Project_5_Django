from django.db import migrations, models
from django.utils.text import slugify


def backfill_product_skus(apps, schema_editor):
    Product = apps.get_model('PickUp', 'Product')

    for product in Product.objects.filter(models.Q(sku__isnull=True) | models.Q(sku='')):
        if product.category_id:
            prefix = slugify(product.category.name or product.category.slug or 'product')[:4].upper() or 'PROD'
        else:
            prefix = 'PROD'

        base_sku = f"{prefix}-{product.pk:05d}"
        sku = base_sku
        suffix = 1

        while Product.objects.filter(sku=sku).exclude(pk=product.pk).exists():
            sku = f"{base_sku}-{suffix}"
            suffix += 1

        product.sku = sku
        product.save(update_fields=['sku'])


class Migration(migrations.Migration):
    dependencies = [
        ('PickUp', '0013_product_sku'),
    ]

    operations = [
        migrations.RunPython(backfill_product_skus, migrations.RunPython.noop),
    ]
