# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoGlobal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notificacoes_habilitadas', models.BooleanField(default=True)),
                ('email_suporte', models.EmailField(blank=True, max_length=255, null=True)),
                ('em_manutencao', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuração Global',
                'verbose_name_plural': 'Configurações Globais',
            },
        ),
    ]
