from django.contrib import admin

from accounts import models

admin.site.register(models.Account)
admin.site.register(models.Transaction)
