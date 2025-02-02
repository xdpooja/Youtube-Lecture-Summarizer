from rest_framework import serializers

class YouTubeURLSerializer(serializers.Serializer):
    video_url = serializers.URLField()
