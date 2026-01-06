from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cameras', '0003_alter_camera_detection_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='camera',
            name='stream_url',
            field=models.CharField(max_length=1000),
        ),
    ]
