from rest_framework import serializers
from .models import TrainingVideo

class TrainingVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingVideo
        fields = ['id', 'title', 'description', 'youtube_url', 'product']