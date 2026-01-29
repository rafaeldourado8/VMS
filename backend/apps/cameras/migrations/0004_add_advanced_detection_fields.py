# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cameras", "0003_alter_camera_detection_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="camera",
            name="roi_areas",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name="camera",
            name="virtual_lines",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name="camera",
            name="tripwires",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name="camera",
            name="zone_triggers",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name="camera",
            name="recording_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="camera",
            name="recording_retention_days",
            field=models.IntegerField(default=30),
        ),
    ]
