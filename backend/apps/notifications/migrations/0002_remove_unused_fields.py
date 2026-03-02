# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationpreference',
            name='detection_alerts',
        ),
        migrations.RemoveField(
            model_name='notificationpreference',
            name='storage_warning',
        ),
        migrations.RemoveField(
            model_name='notificationpreference',
            name='daily_report',
        ),
        migrations.RemoveField(
            model_name='notificationpreference',
            name='daily_report_time',
        ),
    ]
