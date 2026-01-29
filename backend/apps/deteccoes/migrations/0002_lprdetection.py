# Generated migration for LPRDetection model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cameras', '0001_initial'),
        ('deteccoes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LPRDetection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_text', models.CharField(db_index=True, max_length=20)),
                ('confidence', models.FloatField()),
                ('bbox', models.JSONField()),
                ('plate_id', models.CharField(max_length=50)),
                ('plate_image_path', models.CharField(max_length=500)),
                ('full_frame_path', models.CharField(max_length=500)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('is_mercosul', models.BooleanField(default=False)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lpr_detections', to='cameras.camera')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='lprdetection',
            index=models.Index(fields=['-timestamp', 'camera'], name='deteccoes_l_timesta_idx'),
        ),
        migrations.AddIndex(
            model_name='lprdetection',
            index=models.Index(fields=['plate_text'], name='deteccoes_l_plate_t_idx'),
        ),
    ]
