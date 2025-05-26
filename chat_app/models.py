from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(blank=True)
    image = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} at {self.timestamp}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    online = models.BooleanField(default=False)
    
    avatar_updated_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Profile.objects.get(pk=self.pk)
            if orig.avatar != self.avatar:
                self.avatar_updated_at = now()
        else:
            self.avatar_updated_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"
