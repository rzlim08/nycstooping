from django.db import models

# Create your models here.


class PostLocation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField()
    display_url = models.TextField()
    id = models.TextField(primary_key=True)
    insta_account = models.TextField()
    caption = models.TextField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ["posted_at"]
