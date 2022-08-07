import uuid
from django.db import models
# read difference  https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#extending-the-existing-user-model     https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model # https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import re

# Manager to create the user
# Here the BaseUserManager is overwritten such that all the relevant functions of manage.py etc refer to it


class UserManager(BaseUserManager):
    '''
    creating a manager for a custom user model

    '''

    def create_user(self, username, email, password, sub_newsletter):
        """
        Create and return a `User` with an email, username and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if password is None:
            raise TypeError('Users must have a password.')
        if len(password) < 7:
            raise ValueError('Password has a minimum length of 7')
        pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$")
        if (not pattern.match(password)):
            raise ValueError(
                'Password requires at least 1 Digit, 1 uppercase and 1 lowercase')

        user = User(
            username=username.lower(),   # all usernames are assumed ot be lower letters
            # make domain part case insensitive
            email=self.normalize_email(email),
            sub_newsletter=sub_newsletter
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        This function is called also in case we do it via manage.py
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if password is None:
            raise TypeError('Superusers must have a password.')
        if len(password) < 7:
            raise ValueError('Password has a minimum length of 7')
        pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).+$")
        if (not pattern.match(password)):
            raise ValueError(
                'Password requires at least 1 Digit, 1 uppercase and 1 lowercase')

        user = self.create_user(username, email, password, True)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


# The general user that django uses for authentication etc
# The django default user is overwritten by this model in the settings.py
class User(AbstractBaseUser):
    # Required Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        max_length=255, unique=True, null=False, blank=False)
    username = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    sub_newsletter = models.BooleanField(default=False)

    # null in case the user is not a stripe customers and the id otherwise
    stripe_customer_id = models.CharField(max_length=100, null=True)

    # Booleans for verification and password reset
    email_confirmed = models.BooleanField(default=False)
    password_reset = models.BooleanField(default=False)

    # Tell django to use email as login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        return '{} - {}'.format(self.username, self.email)

