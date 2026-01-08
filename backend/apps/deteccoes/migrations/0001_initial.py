from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True

    dependencies = [("cameras", "0003_alter_camera_detection_settings")]

    operations = [
        migrations.CreateModel(
            name="Deteccao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "plate",
                    models.CharField(
                        blank=True, db_index=True, max_length=20, null=True
                    ),
                ),
                ("confidence", models.FloatField(blank=True, null=True)),
                ("timestamp", models.DateTimeField(db_index=True)),
                (
                    "vehicle_type",
                    models.CharField(
                        choices=[
                            ("car", "Carro"),
                            ("motorcycle", "Motocicleta"),
                            ("truck", "Caminhão"),
                            ("bus", "Ônibus"),
                            ("unknown", "Desconhecido"),
                        ],
                        default="unknown",
                        max_length=20,
                    ),
                ),
                ("image_url", models.CharField(blank=True, max_length=1000, null=True)),
                ("video_url", models.CharField(blank=True, max_length=1000, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "camera",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deteccoes",
                        to="cameras.camera",
                    ),
                ),
            ],
            options={
                "verbose_name": "Detecção",
                "verbose_name_plural": "Detecções",
                "ordering": ["-timestamp"],
            },
        )
    ]
