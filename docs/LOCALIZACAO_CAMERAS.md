# Sistema de Localização de Câmeras

## Formatos Suportados

O sistema agora aceita **3 formatos** de localização para câmeras:

### 1. Endereço Estruturado
Campos individuais para endereço completo:
- **Rua** (address_street)
- **Número** (address_number)
- **Bairro** (address_neighborhood)
- **Cidade** (address_city) - obrigatório
- **Estado** (address_state) - UF com 2 letras

**Exemplo:**
```
Rua: Av. Paulista
Número: 1578
Bairro: Bela Vista
Cidade: São Paulo
Estado: SP
```

### 2. Coordenadas Geográficas
Latitude e longitude em formato decimal:
- **Latitude** (latitude)
- **Longitude** (longitude)

**Exemplo:**
```
Latitude: -23.561414
Longitude: -46.656139
```

### 3. URL do Google Maps
Cole diretamente a URL do Google Maps:
- **URL** (maps_url)
- O sistema extrai automaticamente as coordenadas

**Formatos aceitos:**
```
https://www.google.com/maps?q=-23.561414,-46.656139
https://maps.google.com/?q=-23.561414,-46.656139
https://www.google.com/maps/@-23.561414,-46.656139,15z
```

## Campos do Banco de Dados

### Modelo Camera
```python
# Campo legado (texto livre)
location = CharField(max_length=1000)

# Endereço estruturado
address_street = CharField(max_length=255, blank=True, null=True)
address_number = CharField(max_length=20, blank=True, null=True)
address_neighborhood = CharField(max_length=100, blank=True, null=True)
address_city = CharField(max_length=100, blank=True, null=True)
address_state = CharField(max_length=2, blank=True, null=True)

# Coordenadas
latitude = FloatField(blank=True, null=True)
longitude = FloatField(blank=True, null=True)

# URL do Google Maps
maps_url = CharField(max_length=1000, blank=True, null=True)
```

## Comportamento do Sistema

### Backend (Serializer)
1. Se `maps_url` for fornecida, extrai coordenadas automaticamente
2. Se campos de endereço forem fornecidos, constrói o campo `location` automaticamente
3. Formato do `location` gerado: "Rua, Número - Bairro - Cidade - Estado"

### Frontend (AddCameraModal)
Interface com 4 modos de entrada:
- **Texto**: Campo livre para texto simples
- **Endereço**: Formulário estruturado com campos separados
- **Coordenadas**: Dois campos numéricos (lat/lng)
- **URL Maps**: Campo para colar URL do Google Maps

## Migration

Execute o script para aplicar as mudanças no banco:
```bash
scripts\apply_location_fields_migration.bat
```

Ou manualmente:
```bash
cd backend
python manage.py makemigrations cameras
python manage.py migrate cameras
```

## Exemplos de Uso

### API - Criar câmera com endereço estruturado
```json
{
  "name": "Câmera Entrada",
  "stream_url": "rtsp://...",
  "address_street": "Av. Paulista",
  "address_number": "1578",
  "address_neighborhood": "Bela Vista",
  "address_city": "São Paulo",
  "address_state": "SP"
}
```

### API - Criar câmera com coordenadas
```json
{
  "name": "Câmera Entrada",
  "stream_url": "rtsp://...",
  "latitude": -23.561414,
  "longitude": -46.656139,
  "location": "Entrada Principal"
}
```

### API - Criar câmera com URL do Google Maps
```json
{
  "name": "Câmera Entrada",
  "stream_url": "rtsp://...",
  "maps_url": "https://www.google.com/maps?q=-23.561414,-46.656139"
}
```

## Compatibilidade

- ✅ Campos antigos continuam funcionando
- ✅ Campo `location` é preenchido automaticamente quando possível
- ✅ Coordenadas são extraídas de URLs do Google Maps
- ✅ Todos os campos são opcionais (exceto `location` ou `address_city`)
