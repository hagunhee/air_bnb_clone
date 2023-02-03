# Generated by Django 4.1.6 on 2023-02-03 18:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_host",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="name",
            field=models.CharField(default="", max_length=150),
        ),
    ]
