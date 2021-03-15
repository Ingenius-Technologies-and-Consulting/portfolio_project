from django.db import models

# Create your models here.
class AssetType(models.Model):
	asset_type = models.CharField(max_length = 128, null = False, blank = False, verbose_name = 'Asset Type')
	description = models.CharField(max_length = 50, null = True, blank = True)
	created_at = models.DateTimeField(auto_now_add = True, editable = False)
	updated_at = models.DateTimeField(auto_now = True)

	def __str__(self):
		return self.asset_type


class Asset(models.Model):
	asset_type = models.ForeignKey(AssetType, on_delete = models.CASCADE)
	asset_symbol = models.CharField(max_length = 50, null = False, blank = False, verbose_name = 'Asset Symbol')
	asset_name = models.CharField(max_length = 128, null = False, blank = False, verbose_name = 'Asset Name')
	asset_exchange = models.CharField(max_length = 128, null = True, blank = True, verbose_name = 'Asset Exchange')
	asset_category = models.CharField(max_length = 128, null = True, blank = True, verbose_name = 'Asset Sector')
	asset_country = models.CharField(max_length = 50, null = False, blank = False, verbose_name = 'Asset Country')

