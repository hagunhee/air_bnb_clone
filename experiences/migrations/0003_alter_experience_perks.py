# Generated by Django 4.1.6 on 2023-02-27 06:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("experiences", "0002_alter_experience_category_alter_experience_host"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experience",
            name="perks",
            field=models.ManyToManyField(
                related_name="experiences", to="experiences.perk"
            ),
        ),
    ]
