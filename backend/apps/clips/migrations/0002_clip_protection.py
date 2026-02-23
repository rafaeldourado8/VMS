# Generated migration for Clip model updates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0001_initial'),  # Ajuste conforme sua última migration
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='camera',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='clips',
                to='cameras.camera'
            ),
        ),
        migrations.AddField(
            model_name='clip',
            name='camera_id_backup',
            field=models.IntegerField(default=0, help_text='ID da câmera para referência histórica'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clip',
            name='camera_name_backup',
            field=models.CharField(default='', help_text='Nome da câmera no momento da criação', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clip',
            name='file_size_bytes',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='clip',
            name='is_protected',
            field=models.BooleanField(default=True, help_text='Protegido contra retenção automática'),
        ),
        migrations.AddField(
            model_name='clip',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='clip',
            name='external_id',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddIndex(
            model_name='clip',
            index=models.Index(fields=['owner', 'created_at'], name='clips_clip_owner_created_idx'),
        ),
        migrations.AddIndex(
            model_name='clip',
            index=models.Index(fields=['external_id'], name='clips_clip_external_idx'),
        ),
        migrations.AddIndex(
            model_name='clip',
            index=models.Index(fields=['is_protected'], name='clips_clip_protected_idx'),
        ),
    ]
