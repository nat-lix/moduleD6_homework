from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post, PostCategory
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.shortcuts import redirect

@receiver(m2m_changed, sender=Post.postCategory.through)
def mailpost_subscribe(sender, instance, **kwargs):
    for category in instance.postCategory.all():
        for sub in category.subscribers.all():
            
            html_content = render_to_string(
                'create_post.html',
                {'post':instance,}
            )
            msg = EmailMultiAlternatives(
                subject=f'{instance.postTitle}',
                body = instance.postText,
                from_email='talathecat@yandex.ru',
                to = [sub.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()