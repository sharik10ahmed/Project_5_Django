from .models import Announcement


def announcements_context(request):
    announcements = Announcement.objects.filter(is_active=True)
    return {
        'announcements': announcements
    }
