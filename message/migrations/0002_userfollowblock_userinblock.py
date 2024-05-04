# Generated by Django 4.1 on 2024-05-04 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("message", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserFollowBlock",
            fields=[
                ("auto_id", models.AutoField(primary_key=True, serialize=False)),
                ("date_followed", models.DateField(blank=True, null=True)),
            ],
            options={
                "db_table": "user_follow_block",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="UserInBlock",
            fields=[
                ("auto_id", models.AutoField(primary_key=True, serialize=False)),
                ("date_joined", models.DateField(blank=True, null=True)),
            ],
            options={
                "db_table": "user_in_block",
                "managed": False,
            },
        ),
    ]