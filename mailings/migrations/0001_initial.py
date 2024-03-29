# Generated by Django 5.0.2 on 2024-02-09 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Mailing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "text",
                    models.TextField(
                        default="Удалите этот текст перед отправкой", null=True
                    ),
                ),
                ("end_time", models.DateTimeField()),
            ],
        ),
    ]
