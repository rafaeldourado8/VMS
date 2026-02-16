# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('location', models.CharField(max_length=1000)),
                ('status', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='online', max_length=10)),
                ('stream_url', models.CharField(max_length=1000, unique=True)),
                ('thumbnail_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('onvif_host', models.CharField(blank=True, help_text='IP ou hostname da câmera', max_length=255, null=True)),
                ('onvif_port', models.IntegerField(default=80, help_text='Porta ONVIF (geralmente 80)')),
                ('onvif_username', models.CharField(blank=True, max_length=255, null=True)),
                ('onvif_password', models.CharField(blank=True, max_length=255, null=True)),
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
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cameras', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
