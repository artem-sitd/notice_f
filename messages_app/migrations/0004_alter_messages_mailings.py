# Generated by Django 5.0.2 on 2024-02-14 10:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailings", "0003_mailing_status"),
        ("messages_app", "0003_messages_errors"),
    ]

    operations = [
        migrations.AlterField(
            model_name="messages",
            name="mailings",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to="mailings.mailing",
            ),
        ),
    ]
