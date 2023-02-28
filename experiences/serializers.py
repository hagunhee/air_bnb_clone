from rest_framework import serializers
from medias.serializers import PhotoSerializer
from .models import Perk, Experience
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer
from wishlists.models import Wishlist


class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"


class ExperienceListSerializer(serializers.ModelSerializer):

    rating = serializers.SerializerMethodField()
    is_host = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:

        model = Experience
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_host",
            "photos",
        )

    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user


class ExperienceDetailSerializer(serializers.ModelSerializer):
    host = TinyUserSerializer(read_only=True)
    perks = PerkSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()
    is_host = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Experience
        fields = "__all__"

    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user

    def get_is_liked(self, experience):
        request = self.context["request"]
        return Wishlist.objects.filter(user=request.user, experiences__id=experience.pk).exists()
