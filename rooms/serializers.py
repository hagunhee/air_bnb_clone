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
            "pk",
            "name",
            "description",
        )


# 면세점에서 구매한 물건을 해외로 재판매할 때 싱가폴, 인도네시아, 말레이시아 , 태국등에서는 면세품을 수입해도 괜찮나?
# 면세점에서 구매한 물건을 위 나라에서 판매할 때 세금을 납부해야 하나?


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
    reviews = ReviewSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = "__all__"

    def get_rating(self, room):
        # 위의 SerializerMethodField()와 필수적 관계이며
        # 인자는 self,와 현재 serializing 하고 있는 오브젝트
        return room.rating()

    def get_is_owner(self, room):
        request = self.context.get("request")
        if request:
            return room.owner == request.user
        return False

    def get_is_liked(self, room):
        request = self.context.get("request")
        if request:
            if request.user.is_authenticated:
                # 룸을 보고 있는 user가 소유한 wishlist들을 찾는다.
                # rooms list안에 사용자가 보고있는 room을 가지고 있는 wishlist를 찾아낸다.
                return Wishlist.objects.filter(user=request.user, rooms__id=room.pk).exists()
        return False
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
