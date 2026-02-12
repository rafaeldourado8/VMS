# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cameras', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mosaico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mosaicos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Clip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('file_path', models.CharField(max_length=1000)),
                ('thumbnail_path', models.CharField(blank=True, max_length=1000, null=True)),
                ('duration_seconds', models.IntegerField()),
                ('external_id', models.CharField(blank=True, max_length=64, null=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clips', to='cameras.camera')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clips', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MosaicoCameraPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(choices=[(1, 'Posição 1'), (2, 'Posição 2'), (3, 'Posição 3'), (4, 'Posição 4')])),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cameras.camera')),
                ('mosaico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clips.mosaico')),
            ],
        ),
        migrations.AddField(
            model_name='mosaico',
            name='cameras',
            field=models.ManyToManyField(related_name='mosaicos', through='clips.MosaicoCameraPosition', to='cameras.camera'),
        ),
        migrations.AlterUniqueTogether(
            name='mosaicocameraposition',
            unique_together={('mosaico', 'position'), ('mosaico', 'camera')},
        ),
    ]
