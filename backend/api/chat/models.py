from ..users.models import User
from django.db import models
import uuid
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sender')        
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recipient')        
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
    class Meta:
        ordering = ('timestamp', )

