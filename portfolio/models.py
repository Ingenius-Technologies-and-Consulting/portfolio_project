from django.db import models
from assets.models import Asset
from users.models import User

# Create your models here.
class Portfolio(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	name = models.CharField(max_length = 128, blank = False, null = False, verbose_name = 'Portfolio Name')
	description = models.CharField(max_length = 128, blank = False, null = False, verbose_name = 'Portfolio Description')

	def __str__(self):
		return self.name

class Transaction(models.Model):

	BUY = 'Buy'
	SELL = 'Sell'
	DIVIDEND = 'Dividend'

	TRANSACTION_TYPES = (
			(BUY, 'Buy'),
			(SELL, 'Sell'),
			(DIVIDEND, 'Dividend')
		)


	portfolio = models.ForeignKey(Portfolio, on_delete = models.CASCADE)
	asset = models.ForeignKey(Asset, on_delete = models.CASCADE)
	transaction_type = models.CharField(max_length = 50, choices = TRANSACTION_TYPES, null = False)
	amount = models.DecimalField(max_digits = 10, decimal_places = 2, null = False)
	transaction_price = models.DecimalField(max_digits = 10, decimal_places = 2)
	transaction_date = models.DateTimeField(null = False)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
