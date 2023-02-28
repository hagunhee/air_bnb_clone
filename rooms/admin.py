from django.contrib import admin
from .models import Room, Amenity


@admin.action(description="Set All prices to zero")
def reset_prices(model_admin, request, rooms):
    # 3개의 매개변수가 필요함
    for room in rooms.all():
        room.price = 0
        room.save()


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    actions = (reset_prices,)
    list_display = (
        "name",
        "price",
        "kind",
        "total_amenities",
        "owner",
        "created_at",
        "rating",
    )

    list_filter = (
        "country",
        "city",
        "price",
        "rooms",
        "toilets",
        "pet_friendly",
        "kind",
        "amenities",
        "created_at",
        "updated_at",
    )

    search_fields = ("owner__username",)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
