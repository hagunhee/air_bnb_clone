from django.db import models
from common.models import CommonModel


class Experience(CommonModel):

    """Experience Model Definition"""

    country = models.CharField(max_length=50, default="한국")
    city = models.CharField(max_length=80, default="서울")
    name = models.CharField(max_length=250)
    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=250)
    start = models.TimeField()
    # TimeField는 시간, 분 , 초만 기억한다.
    end = models.TimeField()
    description = models.TextField()
    perks = models.ManyToManyField(
        "experiences.Perk",
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="experiences",
    )
    # 카테고리가 삭제되더라도 카스케이드하지 않고 비워둠.
    def __str__(self) -> str:
        return self.name


class Perk(CommonModel):

    """What is included on an Experience"""

    name = models.CharField(
        max_length=100,
    )
    details = models.CharField(
        max_length=250,
        blank=True,
        null=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.name
