from rest_framework import serializers
from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from reviews.serializers import ReviewSerializer
from categories.serializers import CategorySerializer
from medias.serializers import PhotoSerializer
from wishlists.models import Wishlist


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = (
            "name",
            "description",
        )


class RoomDetailSerializer(serializers.ModelSerializer):

    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(
        many=True,
        read_only=True,
    )
    category = CategorySerializer(
        read_only=True,
    )
    rating = serializers.SerializerMethodField()
    # 아래의 get_xxxxx와 한 쌍이다.
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    def get_rating(self, room):
        # 위의 SerializerMethodField()와 필수적 관계이며
        # 인자는 self,와 현재 serializing 하고 있는 오브젝트
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        return room.owner == request.user

    def get_is_liked(self, room):
        request = self.context["request"]
        # 룸을 보고 있는 user가 소유한 wishlist들을 찾는다.
        # rooms list안에 사용자가 보고있는 room을 가지고 있는 wishlist를 찾아낸다.
        return Wishlist.objects.filter(user=request.user, rooms__id=room.pk).exists()
        # user가 만든 wishlist중에 room id가 있는 room list를 포함한 wishlist를 찾아 유무를 확인해준다.


class RoomListSerializer(serializers.ModelSerializer):

    rating = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
            "photos",
        )

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        return room.owner == request.user
