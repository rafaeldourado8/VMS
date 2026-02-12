# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cameras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deteccao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(db_index=True, help_text='Texto da placa detectada', max_length=20)),
                ('confianca', models.FloatField(default=0.0, help_text='Confiança do OCR (0.0 a 1.0)')),
                ('snapshot_path', models.CharField(help_text='Caminho relativo: media/snapshots/YYYY/MM/DD/filename.jpg', max_length=500)),
                ('vehicle_type', models.CharField(choices=[('car', 'Carro'), ('motorcycle', 'Motocicleta'), ('truck', 'Caminhão'), ('bus', 'Ônibus'), ('unknown', 'Desconhecido')], default='unknown', max_length=20)),
                ('data_hora', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(help_text='Câmera que originou esta detecção.', on_delete=django.db.models.deletion.CASCADE, related_name='deteccoes', to='cameras.camera')),
            ],
            options={
                'verbose_name': 'Detecção',
                'verbose_name_plural': 'Detecções',
                'ordering': ['-data_hora'],
            },
        ),
        migrations.AddIndex(
            model_name='deteccao',
            index=models.Index(fields=['camera', '-data_hora'], name='deteccoes_d_camera__idx'),
        ),
        migrations.AddIndex(
            model_name='deteccao',
            index=models.Index(fields=['placa', '-data_hora'], name='deteccoes_d_placa_idx'),
        ),
    ]
