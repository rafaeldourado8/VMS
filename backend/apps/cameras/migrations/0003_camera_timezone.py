# Generated migration
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('cameras', '0002_camera_address_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='timezone',
            field=models.CharField(default='America/Sao_Paulo', max_length=50),
        ),
    ]
