from rest_framework import serializers


class FacebookScrupperSerializer(serializers.Serializer):
    post_url = serializers.CharField(max_length=250, required=True)
