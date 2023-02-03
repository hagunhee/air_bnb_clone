from django.contrib import admin
from .models import House


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "address",
        ("price_per_night", "pets_allowed"),
    )  # 튜플을 사용해 묶음.
    list_display = ("name", "price_per_night", "address", "pets_allowed")
    list_filter = ("price_per_night", "pets_allowed")
    search_fields = ("address", "name")
    list_display_links = ("name", "address")  # 타고 들어갈 수 있는 항목을 늘려줌. 기존은 오직 name이였다.
    list_editable = ("pets_allowed",)
