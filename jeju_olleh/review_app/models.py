from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Review(models.Model):
    content = models.TextField()
    rate = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)