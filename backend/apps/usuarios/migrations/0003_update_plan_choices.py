# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='plan',
            field=models.CharField(
                choices=[
                    ('basic', 'Basic - 7 dias'),
                    ('pro', 'Pro - 15 dias'),
                    ('premium', 'Premium - 30 dias')
                ],
                default='basic',
                max_length=20
            ),
        ),
    ]
