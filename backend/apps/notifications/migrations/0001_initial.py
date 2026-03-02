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
            name='LoginLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('logged_in_at', models.DateTimeField(auto_now_add=True, verbose_name='Login em')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_logs', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Log de Login',
                'verbose_name_plural': 'Logs de Login',
                'db_table': 'login_logs',
                'ordering': ['-logged_in_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_alerts', models.BooleanField(default=True, verbose_name='Alertas por Email')),
                ('push_notifications', models.BooleanField(default=False, verbose_name='Notificações Push')),
                ('detection_alerts', models.BooleanField(default=True, verbose_name='Alertas de Detecção LPR')),
                ('camera_offline', models.BooleanField(default=True, verbose_name='Alertas de Câmera Offline')),
                ('system_alerts', models.BooleanField(default=True, verbose_name='Alertas do Sistema')),
                ('storage_warning', models.BooleanField(default=True, verbose_name='Avisos de Armazenamento')),
                ('daily_report', models.BooleanField(default=False, verbose_name='Relatório Diário')),
                ('daily_report_time', models.TimeField(default='08:00:00', verbose_name='Horário do Relatório')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Preferência de Notificação',
                'verbose_name_plural': 'Preferências de Notificação',
                'db_table': 'notification_preferences',
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('email', 'Email'), ('push', 'Push'), ('sms', 'SMS')], max_length=20, verbose_name='Tipo')),
                ('category', models.CharField(choices=[('detection', 'Detecção LPR'), ('camera_offline', 'Câmera Offline'), ('system', 'Sistema'), ('storage', 'Armazenamento'), ('daily_report', 'Relatório Diário')], max_length=50, verbose_name='Categoria')),
                ('title', models.CharField(max_length=255, verbose_name='Título')),
                ('message', models.TextField(verbose_name='Mensagem')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Lido em')),
                ('success', models.BooleanField(default=True, verbose_name='Sucesso')),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='Mensagem de Erro')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Log de Notificação',
                'verbose_name_plural': 'Logs de Notificações',
                'db_table': 'notification_logs',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AddIndex(
            model_name='loginlog',
            index=models.Index(fields=['user', '-logged_in_at'], name='login_logs_user_id_c51ec5_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['user', '-sent_at'], name='notificati_user_id_8b2ede_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationlog',
            index=models.Index(fields=['category', '-sent_at'], name='notificati_categor_f6deca_idx'),
        ),
    ]
