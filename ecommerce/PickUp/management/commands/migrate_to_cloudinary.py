import os
import re

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand

from PickUp.models import Product, User


cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'),
    api_key=settings.CLOUDINARY_STORAGE.get('API_KEY'),
    api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET'),
)


def _extract_public_id_from_url(url):
    # Cloudinary image storage fields should store the public_id rather than the full secure URL.
    match = re.search(r'/upload/(?:v\d+/)?(?P<public_id>.+)$', url)
    if not match:
        return None

    public_id = match.group('public_id')
    # Remove any query string or signature parameters.
    public_id = public_id.split('?')[0]
    return public_id


class Command(BaseCommand):
    help = 'Upload existing local product and user profile images to Cloudinary and update the model fields.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting Cloudinary media migration...'))

        migrated_products = self.migrate_products()
        migrated_users = self.migrate_users()

        self.stdout.write(
            self.style.SUCCESS(
                f'Cloudinary migration complete. Migrated {migrated_products} products and {migrated_users} user profiles.'
            )
        )

    def migrate_products(self):
        products = Product.objects.exclude(image__isnull=True).exclude(image='')
        migrated_count = 0

        for product in products:
            if self._migrate_image_field(product, 'image', 'product'):
                migrated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Finished processing {migrated_count} products.'))
        return migrated_count

    def migrate_users(self):
        users = User.objects.exclude(profile_image__isnull=True).exclude(profile_image='')
        migrated_count = 0

        for user in users:
            if self._migrate_image_field(user, 'profile_image', 'user profile'):
                migrated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Finished processing {migrated_count} user profiles.'))
        return migrated_count

    def _migrate_image_field(self, instance, field_name, label):
        current_value = getattr(instance, field_name)

        if not current_value:
            return False

        image_name = current_value.name if hasattr(current_value, 'name') else str(current_value)

        if isinstance(image_name, str) and image_name.startswith(('http://', 'https://')):
            public_id = _extract_public_id_from_url(image_name)
            if public_id:
                if _cloudinary_resource_exists(public_id):
                    setattr(instance, field_name, public_id)
                    instance.save(update_fields=[field_name])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Repaired {label} "{instance}" by converting stored Cloudinary URL to public_id: {public_id}'
                        )
                    )
                    return True

                local_file = _find_local_file_by_basename(os.path.basename(public_id))
                if local_file:
                    upload_result = _upload_local_file(local_file)
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {label} "{instance}" because the stored Cloudinary URL could not be verified and the local file was not found.'
                        )
                    )
                    return False
        else:
            file_path = os.path.join(str(settings.MEDIA_ROOT), image_name)
            if os.path.exists(file_path):
                upload_result = _upload_local_file(file_path)
            else:
                local_file = _find_local_file_by_basename(os.path.basename(image_name))
                if local_file:
                    upload_result = _upload_local_file(local_file)
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {label} "{instance}" because the local file was not found at {file_path} and could not be located by filename.'
                        )
                    )
                    return False

        public_id = _extract_public_id_from_url(upload_result.get('secure_url', ''))
        if public_id:
            setattr(instance, field_name, public_id)
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Uploaded {label} "{instance}" but could not extract a Cloudinary public_id; saving the full secure_url instead.'
                )
            )
            setattr(instance, field_name, upload_result.get('secure_url', ''))

        instance.save(update_fields=[field_name])

        self.stdout.write(
            self.style.SUCCESS(
                f'Uploaded {label} "{instance}" to Cloudinary: {upload_result["secure_url"]}'
            )
        )
        return True


def _cloudinary_resource_exists(public_id):
    try:
        cloudinary.api.resource(public_id)
        return True
    except Exception:
        return False


def _find_local_file_by_basename(basename):
    media_root = str(settings.MEDIA_ROOT)
    basename_no_ext, ext = os.path.splitext(basename)
    candidate_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    for root, _, files in os.walk(media_root):
        for filename in files:
            name_no_ext, file_ext = os.path.splitext(filename)
            if name_no_ext == basename_no_ext and file_ext.lower() in candidate_extensions:
                return os.path.join(root, filename)
    return None


def _upload_local_file(file_path):
    with open(file_path, 'rb') as image_file:
        return cloudinary.uploader.upload(
            image_file,
            resource_type='image',
            folder='migrated-media',
            overwrite=False,
            use_filename=True,
            unique_filename=False,
        )
