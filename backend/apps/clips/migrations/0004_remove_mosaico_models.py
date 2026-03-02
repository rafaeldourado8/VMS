# Generated manually to safely remove Mosaico models

from django.db import migrations


def remove_mosaico_tables(apps, schema_editor):
    """Safely remove Mosaico tables if they exist"""
    from django.db import connection
    
    # Skip if tables don't exist (fresh database)
    with connection.cursor() as cursor:
        try:
            if connection.vendor == 'sqlite':
                cursor.execute("DROP TABLE IF EXISTS clips_mosaicocameraposition;")
                cursor.execute("DROP TABLE IF EXISTS clips_mosaico;")
            else:
                cursor.execute("DROP TABLE IF EXISTS clips_mosaicocameraposition CASCADE;")
                cursor.execute("DROP TABLE IF EXISTS clips_mosaico CASCADE;")
        except Exception:
            pass  # Tables don't exist, skip


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0003_rename_indexes'),
    ]

    operations = [
        # First, drop the tables if they exist
        migrations.RunPython(remove_mosaico_tables, migrations.RunPython.noop),
        # Then update the state without touching the database
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='mosaicocameraposition',
                    name='mosaico',
                ),
                migrations.RemoveField(
                    model_name='mosaicocameraposition',
                    name='camera',
                ),
                migrations.DeleteModel(
                    name='MosaicoCameraPosition',
                ),
                migrations.RemoveField(
                    model_name='mosaico',
                    name='cameras',
                ),
                migrations.RemoveField(
                    model_name='mosaico',
                    name='owner',
                ),
                migrations.DeleteModel(
                    name='Mosaico',
                ),
            ],
            database_operations=[],
        ),
    ]
