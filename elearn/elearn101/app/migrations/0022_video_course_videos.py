# Generated by Django 4.1.4 on 2024-04-30 12:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0021_questionpaper"),
    ]

    operations = [
        migrations.CreateModel(
            name="Video",
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
                ("title", models.CharField(max_length=100)),
                ("file", models.FileField(upload_to="staticfiles/demo_videos/")),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="videos",
            field=models.ManyToManyField(to="app.video"),
        ),
    ]
