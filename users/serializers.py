from rest_framework.serializers import ModelSerializer
from .models import User


class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "username",
        )


class PrivateUserSerializer(ModelSerializer):
    # django rest framework와 ModelSerialzer 를 사용하는게 좋은 이유는
    # uniqueness를 계쏙 체크해주기 때문.(id나 email이 이미 존재하는가? 등.)
    class Meta:
        model = User
        exclude = (
            "password",
            "is_superuser",
            "is_staff",
            "id",
            "is_active",
            "first_name",
            "last_name",
            "groups",
            "user_permissions",
        )
