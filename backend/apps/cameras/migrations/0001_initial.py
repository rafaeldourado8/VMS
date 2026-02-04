from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='online', max_length=10)),
                ('stream_url', models.CharField(max_length=1000, unique=True)),
                ('thumbnail_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('detection_settings', models.JSONField(blank=True, default=dict, null=True)),
                ('roi_areas', models.JSONField(blank=True, default=list, null=True)),
                ('virtual_lines', models.JSONField(blank=True, default=list, null=True)),
                ('tripwires', models.JSONField(blank=True, default=list, null=True)),
                ('zone_triggers', models.JSONField(blank=True, default=list, null=True)),
                ('recording_enabled', models.BooleanField(default=True)),
                ('recording_retention_days', models.IntegerField(default=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_path', models.CharField(help_text='Caminho: /recordings/cam_X/YYYY-MM-DD_HH-MM-SS.mp4', max_length=500)),
                ('duration_seconds', models.IntegerField(default=0)),
                ('file_size_bytes', models.BigIntegerField(default=0)),
                ('snapshot_cached', models.ImageField(blank=True, null=True, upload_to='recording_snapshots/%Y/%m/%d/')),
                ('started_at', models.DateTimeField(db_index=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recordings', to='cameras.camera')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.AddIndex(
            model_name='recording',
            index=models.Index(fields=['camera', '-started_at'], name='cameras_rec_camera_idx'),
        ),
    ]
