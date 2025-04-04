from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='') 
    date = models.DateField()
    def __str__(self):
        return f"{self.id}: {self.title}"
    
class Comment(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)