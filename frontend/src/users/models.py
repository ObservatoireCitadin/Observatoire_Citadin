from django.db import models
from django.contrib.auth.models import User
from compare.models import Ville
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    # Necessary information
    # User includes ()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
#    is_list = models.BooleanField(default=False)


    # Updating your user with other things that are not really necessary.
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    # Additional fields
    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
