# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cameras', '0003_alter_camera_detection_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deteccao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(max_length=20, db_index=True, help_text='Texto da placa detectada')),
                ('confianca', models.FloatField(default=0.0, help_text='Confiança do OCR (0.0 a 1.0)')),
                ('snapshot_path', models.CharField(max_length=500, help_text='Caminho relativo: media/snapshots/YYYY/MM/DD/filename.jpg')),
                ('vehicle_type', models.CharField(max_length=20, choices=[('car', 'Carro'), ('motorcycle', 'Motocicleta'), ('truck', 'Caminhão'), ('bus', 'Ônibus'), ('unknown', 'Desconhecido')], default='unknown')),
                ('data_hora', models.DateTimeField(default=timezone.now, db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deteccoes', to='cameras.camera', help_text='Câmera que originou esta detecção.')),
            ],
            options={
                'verbose_name': 'Detecção',
                'verbose_name_plural': 'Detecções',
                'ordering': ['-data_hora'],
                'indexes': [
                    models.Index(fields=['camera', '-data_hora'], name='deteccoes_d_camera__idx'),
                    models.Index(fields=['placa', '-data_hora'], name='deteccoes_d_placa_i_idx'),
                ],
            },
        ),
    ]
