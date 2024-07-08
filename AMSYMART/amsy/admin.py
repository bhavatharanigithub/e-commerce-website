from django.contrib import admin
from .models import *
'''class categoryAdmin(admin.ModelAdmin):
    list_display=('name','image', 'description') if you want you may change by adding parameter to down function with category'''
admin.site.register(Category)
admin.site.register(Product)
# Register your models here.
