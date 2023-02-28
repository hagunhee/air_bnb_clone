from rest_framework import serializers
from users.serializers import TinyUserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):

    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Review
        # request.data에 유저가 없는 상태로 내 시리얼라이저가 유효하기 위해선,
        # read_only = True를 해줘야 페이로드와 평점만 전송해도 유효하다
        fields = (
            "id",
            "user",
            "payload",
            "rating",
        )
