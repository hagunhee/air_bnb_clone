from rest_framework import serializers
from .models import Category


# {"name":"Category from DRF","kind":"rooms"}
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "kind", "pk")
