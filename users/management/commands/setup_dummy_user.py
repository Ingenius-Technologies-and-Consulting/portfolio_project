import random 
import string 

from django.core.management.base import BaseCommand

from users.models import User

def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

class Command(BaseCommand):
	"""
	Update stock tickers
	"""
	def handle(self, *args, **kwargs):
		email = random_char(10) + '@gmail.com'
		new_user = User.manager.create_user(email = email, name = 'test_user', password = 'test1234')
		