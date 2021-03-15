from django.contrib import admin
from assets.models import AssetType, Asset

# Register your models here.
class AssetTypeAdmin(admin.ModelAdmin):
	pass

class AssetAdmin(admin.ModelAdmin):
	pass

admin.site.register(AssetType, AssetTypeAdmin)
admin.site.register(Asset, AssetAdmin)
