from math import log
from django.contrib.auth.models import User

def ranked_reviewers(authors, existing_reviewers=None):
    "Returns a list of possible reviewers, sorted by score"
    author_ids = [author.id for author in authors]
    candidates = User.objects.filter(profile__is_reviewer=True).exclude(id__in=author_ids)
    if existing_reviewers:
        existing_reviewer_ids = [r.id for r in existing_reviewers]
        candidates = candidates.exclude(id__in=existing_reviewer_ids)
    return sorted(candidates.all(), key=lambda c: reviewer_heuristic(authors, c), reverse=True)

def reviewer_heuristic(authors, potential_reviewer):
    "Returns a score for an (author, reviewer) pair"
    factors = {
        'log_total_reviews': log(1 + potential_reviewer.reviews.count()),
        'log_author_reviews': log(1 + potential_reviewer.reviews.filter(
                revision__manuscript__authors__in=authors).count())
    }
    weights = {
        'log_total_reviews': -1,
        'log_author_reviews': -5,
    }
    return sum([factors[key] * weights[key] for key in factors.keys()])
