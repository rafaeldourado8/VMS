# Generated manually to safely remove Mosaico models

from django.db import migrations


def remove_mosaico_tables(apps, schema_editor):
    """Safely remove Mosaico tables if they exist"""
    with schema_editor.connection.cursor() as cursor:
        # Check and drop MosaicoCameraPosition table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'clips_mosaicocameraposition'
            );
        """)
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE clips_mosaicocameraposition CASCADE;")
        
        # Check and drop Mosaico table
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'clips_mosaico'
            );
        """)
        if cursor.fetchone()[0]:
            cursor.execute("DROP TABLE clips_mosaico CASCADE;")


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
