from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cameras', '0005_camera_ai_enabled_camera_recording_enabled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='stream_url',
            field=models.CharField(max_length=1000, unique=True),
        ),
        migrations.AddConstraint(
            model_name='camera',
            constraint=models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_camera_name_per_owner'
            ),
        ),
    ]
