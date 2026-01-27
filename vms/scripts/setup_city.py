from shared.admin.cidades.models import City
from shared.admin.cidades.enums import CityStatus, Plan
city, created = City.objects.get_or_create(
    name='São Paulo',
    defaults={'status': CityStatus.ACTIVE, 'plan': Plan.PREMIUM}
)
print(f'✓ City: {city.name} (ID: {city.id})')
