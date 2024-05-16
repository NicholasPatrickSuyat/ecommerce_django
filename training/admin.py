from django.contrib import admin

from django.contrib import admin
from .models import TrainingVideo

class TrainingVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'youtube_url')
    search_fields = ('title', 'product__title')

admin.site.register(TrainingVideo, TrainingVideoAdmin)
