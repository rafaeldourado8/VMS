from shared.admin.cameras.models import Camera

print("\n=== Câmeras Cadastradas ===\n")
for camera in Camera.objects.all():
    print(f"Nome: {camera.name}")
    print(f"Public ID: {camera.public_id}")
    print(f"Protocol: {camera.protocol}")
    print(f"Active: {camera.is_active}")
    print("-" * 50)
