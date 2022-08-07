from django.db import models

# Create your models here.
class NewsletterMail(models.Model):
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
