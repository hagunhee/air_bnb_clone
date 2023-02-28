from rest_framework.serializers import ModelSerializer
from rooms.serializers import RoomListSerializer
from .models import Wishlist
from experiences.serializers import ExperienceListSerializer


class WishlistSerializer(ModelSerializer):

    rooms = RoomListSerializer(
        many=True,
        read_only=True,
    )

    experiences = ExperienceListSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Wishlist
        fields = [
            "pk",
            "name",
            "rooms",
            "experiences",
        ]
