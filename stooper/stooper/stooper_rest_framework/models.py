from django.db import models

# Create your models here.


class PostLocation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(null=True)
    display_url = models.TextField()
    id = models.TextField(primary_key=True)
    insta_account = models.TextField()
    caption = models.TextField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    accessibility_field = models.TextField(null=True)
    location_text = models.TextField(default="")
    pred_location = models.TextField(default="")
    short_code = models.TextField(default="")


    class Meta:
        ordering = ["posted_at"]
