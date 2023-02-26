from django.contrib import admin
from .models import Review


class ScoreFilter(admin.SimpleListFilter):
    title = "Filter by Score!"
    parameter_name = "score"

    def lookups(self, request, model_admin):
        return [("bad", "Bad"), ("good", "Good")]

    def queryset(self, request, reviews):
        score = self.value()
        if score == "bad":
            return reviews.filter(rating__lt=3)
        else:
            return reviews.filter(rating__gte=3)


class WordFilter(admin.SimpleListFilter):
    title = "Filter by words!"
    parameter_name = "word"

    def lookups(self, request, model_admin):
        return [("good", "Good"), ("great", "Great"), ("awesoem", "Awesome")]

    def queryset(self, request, reviews):
        word = self.value()
        if word:
            return reviews.filter(payload__contains=word)
        else:
            reviews


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "payload",
    )
    list_filter = (
        ScoreFilter,
        WordFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly",
    )
