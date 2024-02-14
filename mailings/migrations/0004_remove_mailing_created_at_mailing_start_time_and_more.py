# Generated by Django 5.0.2 on 2024-02-14 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailings", "0003_mailing_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mailing",
            name="created_at",
        ),
        migrations.AddField(
            model_name="mailing",
            name="start_time",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="mailing",
            name="end_time",
            field=models.DateTimeField(null=True),
        ),
    ]
