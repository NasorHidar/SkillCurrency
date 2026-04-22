from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')
        all_notifications = request.user.notifications.all().order_by('-created_at')[:10]
        return {
            'unread_notifications_count': unread_notifications.count(),
            'notifications': all_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'notifications': [],
    }
