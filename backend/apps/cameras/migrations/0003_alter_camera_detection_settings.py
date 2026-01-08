from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("cameras", "0002_alter_camera_stream_url_alter_camera_thumbnail_url")
    ]

    operations = [
        migrations.AlterField(
            model_name="camera",
            name="detection_settings",
            field=models.JSONField(blank=True, default=dict, null=True),
        )
    ]
