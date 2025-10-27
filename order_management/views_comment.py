"""
コメント・通知機能のビュー
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Project, Comment, Notification
import json


@login_required
@require_POST
def post_comment(request, project_id):
    """コメントを投稿"""
    project = get_object_or_404(Project, pk=project_id)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        is_important = data.get('is_important', False)

        if not content:
            return JsonResponse({'error': 'コメント内容を入力してください'}, status=400)

        comment = Comment.objects.create(
            project=project,
            author=request.user,
            content=content,
            is_important=is_important
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'is_important': comment.is_important,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_GET
def get_comments(request, project_id):
    """案件のコメント一覧を取得"""
    project = get_object_or_404(Project, pk=project_id)
    comments = project.comments.select_related('author').all()

    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'is_important': comment.is_important,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse({
        'comments': comments_data
    })


@login_required
@require_GET
def get_notifications(request):
    """ユーザーの通知一覧を取得"""
    notifications = request.user.notifications.select_related(
        'related_project', 'related_comment'
    ).all()[:20]  # 最新20件

    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'link': notification.link,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    # 未読数も返す
    unread_count = request.user.notifications.filter(is_read=False).count()

    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """通知を既読にする"""
    notification = get_object_or_404(
        Notification,
        pk=notification_id,
        recipient=request.user
    )
    notification.is_read = True
    notification.save()

    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """全ての通知を既読にする"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
