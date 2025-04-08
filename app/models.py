from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class PlaceMode(models.Model):
    place_id = models.IntegerField(null=True, blank=True)
    Name = models.CharField(max_length=200, null=True, blank=True)
    City = models.CharField(max_length=200, blank=True, null=True)
    Zone = models.CharField(max_length=200, blank=True, null=True)
    Type = models.CharField(max_length=200, blank=True, null=True)
    State = models.CharField(max_length=200, null=True, blank=True)
    Description = models.TextField(max_length=1000, null=True, blank=True)  # Changed to TextField for better handling of long text
    Year = models.CharField(max_length=200, null=True, blank=True)
    Time_needed = models.CharField(max_length=200, null=True, blank=True)
    Google_rating = models.CharField(max_length=200, null=True, blank=True)
    Significance = models.CharField(max_length=200, null=True, blank=True)
    Best_time_to_visit = models.CharField(max_length=200, null=True, blank=True)
    Fees = models.CharField(max_length=200, null=True, blank=True)
    Image_url = models.URLField(max_length=30000, null=True, blank=True)
    map_url = models.TextField(null=True, blank=True, db_column="map_url")
    # Removed circular reference to CrowdModel

    def __str__(self):
        return self.Name

# Consolidated Profile model with all necessary fields
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    fav_type = models.CharField(max_length=200, null=True, blank=True)
    fav_significance = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    trophies = models.IntegerField(null=True, blank=True, default=0)
    
    def __str__(self):
        return f"{self.user.username}'s profile" if self.user else "Profile (no user)"
    
    def update_trophies(self):
        """
        Update trophy count based on number of reviews:
        - 1st trophy: 10 reviews
        - 2nd trophy: 25 reviews
        - 3rd trophy: 50 reviews
        - 4th trophy: 100 reviews
        """
        from django.db.models import Count
        
        if not self.user:
            return
            
        # Count user's reviews
        review_count = TripReview.objects.filter(user=self.user).count()
        
        # Calculate trophy count based on review count
        if review_count >= 100:
            self.trophies = 4
        elif review_count >= 50:
            self.trophies = 3
        elif review_count >= 25:
            self.trophies = 2
        elif review_count >= 10:
            self.trophies = 1
        else:
            self.trophies = 0
            
        self.save()

class CrowdModel(models.Model):
    location = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True, related_name='crowd_data')
    month = models.IntegerField(null=True, blank=True)
    crowd_count = models.IntegerField(null=True, blank=True)
    month_name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('location', 'month')

    def __str__(self):
        return f"Crowd data for {self.location} in {self.month_name}" if self.location else "Crowd data (no location)"

class ReviewModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True)
    review_text = models.CharField(max_length=50, null=True, blank=True)
    review_description = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"user {self.user.username}'s review to {self.place.Name}"

class TripReview(models.Model):
    TRAVEL_MEDIUM_CHOICES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('ship', 'Ship'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(PlaceMode, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    travel_medium = models.CharField(max_length=10, choices=TRAVEL_MEDIUM_CHOICES, null=True, blank=True)
    travel_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accommodation_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    food_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_people = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    # Removed image_url field

    def __str__(self):
        return self.title

# ProfileModel has been consolidated with Profile model



