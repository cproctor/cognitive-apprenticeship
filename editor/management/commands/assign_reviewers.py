from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from author.models import Manuscript
from reviewer.models import Review
from reviewer.assignment import ranked_reviewers
from reviewer.email import notify_user_when_review_created

class Command(BaseCommand):
    help = 'Assign reviewers to a manuscript'

    def add_arguments(self, parser):
        parser.add_argument('manuscript_id', type=int)
        parser.add_argument('--clear', action='store_true', help="Clear existing reviewers")
        parser.add_argument('-d', '--days', type=int, help="Days to review")

    def handle(self, *args, **options):
        try: 
            m = Manuscript.objects.get(id=options['manuscript_id'])
        except Manuscript.DoesNotExist:
            raise CommandError("Manuscript not found")
        if options['clear']:
            Review.objects.filter(revision__manuscript=m).all().delete()
            m.reviewers.clear()
        else:
            if m.reviewers.count() > 0:
                msg = "Manuscript {} already has reviewers. Use --clear to remove them."
                raise CommandError(msg.format(m.id))
        reviewers = ranked_reviewers(m.authors.all())
        if len(reviewers) >= settings.NUMBER_OF_REVIEWERS:
            days_until_due = options.get('days') or settings.DAYS_TO_REVIEW
            date_due = timezone.now() + timedelta(days=days_until_due)
            for reviewer in reviewers[:settings.NUMBER_OF_REVIEWERS]:
                m.reviewers.add(reviewer)
                review = Review(
                    revision=m.revisions.last(),
                    reviewer=reviewer,
                    date_due=date_due,
                )
                review.save()
                notify_user_when_review_created(review)
        else:
            msg = "Not enough reviewers for manuscript {}".format(rev.manuscript_id)
            raise CommandError(msg)
