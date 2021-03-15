import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class UserManager(BaseUserManager):
	"""
	Manager for custom user model
	"""
	def create_user(self, email: str, name: str, password: str) -> 'User':
		new_user = self.model(email = email, name = name)
		new_user.set_password(password)
		new_user.save()
		return new_user

	def create_superuser(self, email: str, name: str, password: str) -> 'User':
		new_user = self.create_user(email = email, name = name, password = password)
		new_user.is_superuser = True
		new_user.is_staff = True
		new_user.save()
		return new_user


class User(AbstractBaseUser, PermissionsMixin):
	"""
	Custom User Model
	"""
	user_id = models.UUIDField(default = uuid.uuid4, null = False, verbose_name = 'User UUID')
	email = models.CharField(max_length = 50, unique = True, null = False, blank = False, verbose_name = 'User email')
	name = models.CharField(max_length = 128, null = False, blank = False, verbose_name = 'User name')
	is_staff = models.BooleanField(default = False)
	is_active = models.BooleanField(default = True)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['name']

	manager = UserManager()
	objects = models.Manager()

	def __str__(self):
		return self.name + '@' + self.email

	class Meta:
		ordering = ('email',)


