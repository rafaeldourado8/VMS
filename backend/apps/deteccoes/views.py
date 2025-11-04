from rest_framework import viewsets, permissions
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, views
from .models import Deteccao
from .serializers import DeteccaoSerializer


# Importante: Usamos ReadOnlyModelViewSet
class DeteccaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite às detecções serem vistas.
    (Seção 4.1 e 4.2 da documentação)

    Opcionalmente, permite filtrar por camera_id.
    Ex: /api/detections/?camera_id=1
    """
    serializer_class = DeteccaoSerializer
    permission_classes = [permissions.IsAuthenticated] # Exige autenticação

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as detecções
        das câmeras que pertencem ao usuário autenticado.
        """
        user = self.request.user

        # 1. Filtra detecções APENAS das câmeras do usuário logado
        queryset = Deteccao.objects.filter(camera__owner=user)

        # 2. (Bônus) Permite filtrar por ID de câmera na URL
        camera_id = self.request.query_params.get('camera_id')
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)

        return queryset
    

class IngestDeteccaoAPIView(APIView):
    """
    Endpoint de Ingestão (POST): Recebe eventos de detecção do worker (Celery/FastAPI).
    Não exige login de usuário final, apenas um token interno.
    """
    # Usamos AllowAny (para permitir POST sem token JWT de usuário), 
    # mas o Celery/Worker terá que enviar uma chave de API na header.
    permission_classes = [permissions.AllowAny]

    authentication_classes = []
    
    def post(self, request, format=None):
        # 1. Cria uma cópia dos dados e adiciona o 'camera_id'
        data = request.data.copy()
        
        # O worker envia o ID da câmera, não o objeto.
        # Precisamos garantir que este ID exista.
        
        # 2. Valida e Serializa os dados
        # O Serializer vai validar se todos os campos estão lá (plate, confidence, timestamp)
        serializer = DeteccaoSerializer(data=data)
        
        # Checa se o JSON enviado é válido
        if serializer.is_valid():
            
            # Aqui, o Celery pode estar enviando o camera_id. 
            # Como o Serializer espera o objeto 'camera' (ForeignKey), fazemos a conversão manual:
            # (Simplificando: vamos focar apenas no salvamento dos campos principais)
            
            # 3. Salva a Detecção
            # O save do ModelSerializer lida com a criação de foreign keys automaticamente
            # se o campo estiver na lista 'fields' do Serializer.
            try:
                # O serializer é ligeiramente diferente para ingestão,
                # então vamos usar o método create direto no modelo:
                
                # Exemplo: O worker envia {..., "camera_id": 5}
                camera_id = data.get('camera_id') 
                if not camera_id:
                     return Response({"camera_id": ["Este campo é obrigatório."]}, status=status.HTTP_400_BAD_REQUEST)

                # Busca a câmera para o FK
                from apps.cameras.models import Camera 
                try:
                    camera_instance = Camera.objects.get(pk=camera_id)
                except Camera.DoesNotExist:
                    return Response({"camera_id": ["Câmera não encontrada."]}, status=status.HTTP_404_NOT_FOUND)
                
                # Salva o evento
                Deteccao.objects.create(
                    camera=camera_instance,
                    plate=data.get('plate'),
                    vehicle_type=data.get('vehicle_type'),
                    confidence=data.get('confidence'),
                    timestamp=data.get('timestamp')
                    # ... outros campos
                )
                
                # Se salvou, retorna 201 Created
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Se a validação do JSON falhar, retorna 400 Bad Request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)