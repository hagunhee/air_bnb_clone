# Generated by Django 4.1.6 on 2023-02-03 18:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(editable=False, max_length=150),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(editable=False, max_length=150),
        ),
    ]
