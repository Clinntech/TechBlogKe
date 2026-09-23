from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Post


class Command(BaseCommand):

    help = "Publish scheduled articles when their scheduled time arrives."

    def handle(self, *args, **kwargs):

        now = timezone.now()

        posts = Post.objects.filter(
            status=Post.Status.SCHEDULED,
            scheduled_at__lte=now,
        )


        count = posts.count()


        for post in posts:

            post.status = Post.Status.PUBLISHED

            post.published_at = now

            post.scheduled_at = None

            post.save()



        self.stdout.write(
            self.style.SUCCESS(
                f"{count} scheduled article(s) published."
            )
        )