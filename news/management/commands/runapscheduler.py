import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import Category, Post, PostCategory, User, Author
from django.urls import reverse
from django.utils import timezone
import datetime
 
 
logger = logging.getLogger(__name__)


def onceaweek_mailing():
    categories = Category.objects.all()
    for category in categories:
        category_posts = Post.objects.filter(
            postCategory__name=category,
            dateCreation__gte=timezone.now() - datetime.timedelta(weeks=1),
        )
        print(category_posts)
        articles = []
        for subscriber in category.subscribers.all():
            articles = list(category_posts)
        
            print(subscriber)
            print(articles)
            html_content = render_to_string(
                'weekly_subscribe.html',
                {
                    'subscriber': subscriber,
                    'articles': articles,
                }
            )

          
            msg = EmailMultiAlternatives(
                subject='Посты за неделю',
                body='',
                from_email='talathecat@yandex.ru',
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            print(html_content)
            print(msg)

 
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        scheduler.add_job(
            onceaweek_mailing,
            trigger=CronTrigger(day="*/7"),
            id="onceaweek_mailing", 
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'onceaweek_mailing'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")