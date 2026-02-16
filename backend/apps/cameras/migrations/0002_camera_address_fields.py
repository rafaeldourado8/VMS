# Generated migration
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('cameras', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='address_street',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='address_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='address_neighborhood',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='address_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='address_state',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='camera',
            name='maps_url',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
