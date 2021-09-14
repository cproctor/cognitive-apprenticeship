from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from datetime import datetime

class Command(BaseCommand):
    help = 'Sends a test email'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--recipient', help='Recipient email', 
                default="testing.django@accounts.chrisproctor.net")

    def handle(self, *args, **kwargs):
        now = datetime.now().isoformat()
        self.stdout.write("Sending test email to {} at {}.".format(
            kwargs['recipient'], 
            now
        ))
        send_mail(
            'Django email test',
            'Sent at {}'.format(now),
            'proctorbot@chrisproctor.net',
            [kwargs['recipient']],
            fail_silently=False,
        )
