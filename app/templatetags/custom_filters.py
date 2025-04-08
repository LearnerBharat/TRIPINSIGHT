from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def times(number):
    return range(number)

@register.filter
def avg_rating(reviews):
    """Calculate the average rating from a queryset of reviews."""
    if not reviews:
        return 0
    
    total = sum(review.rating or 0 for review in reviews)
    return total / len(reviews) if len(reviews) > 0 else 0

@register.filter
def filter_by_rating(reviews, rating):
    """Filter reviews by a specific rating."""
    return [review for review in reviews if review.rating == rating]

@register.filter
def rating_percentage(reviews, rating):
    """Calculate the percentage of reviews with a specific rating."""
    if not reviews:
        return 0
    
    rating_count = len([review for review in reviews if review.rating == rating])
    return int((rating_count / len(reviews)) * 100) if len(reviews) > 0 else 0