from django.db import models


class CommonModel(models.Model):

    """Common Model Definition"""

    created_at = models.DateTimeField(auto_now_add=True)

    # 필드의 값을 해당 object가 처음 생성되었을 때 시간으로 설정
    updated_at = models.DateTimeField(auto_now=True)
    # object가 저장될 때마다 해당 필드를 현재 date로 설정

    class Meta:
        abstract = True
