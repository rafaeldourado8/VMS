from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Trunc
from django.db.models import Count, Sum, F # <-- Importações de Agregação

# Importamos os modelos de outros apps
from apps.deteccoes.models import Deteccao

class VehicleTypesAPIView(APIView):
    """
    Endpoint 5.3: Tipos de Veículos
    Retorna a contagem e porcentagem de cada tipo de veículo.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user

        # 1. Filtra todas as detecções que pertencem às câmeras DO USUÁRIO.
        detections_queryset = Deteccao.objects.filter(camera__owner=user)

        # 2. Calcula o número total de todas as detecções (para calcular a porcentagem)
        total_detections = detections_queryset.count()

        # Se não houver detecções, retorna uma lista vazia
        if total_detections == 0:
            return Response({"data": []}, status=200)

        # 3. Agregação: Agrupa por 'vehicle_type' e conta cada grupo.
        data_by_type = detections_queryset.values('vehicle_type').annotate(
            count=Count('vehicle_type') # 'count' é o nome da nova coluna
        )

        # 4. Formata a resposta (Adicionando a Porcentagem)
        response_data = []
        for item in data_by_type:
            count = item['count']
            percentage = (count / total_detections) * 100

            response_data.append({
                "type": item['vehicle_type'],
                "count": count,
                "percentage": round(percentage, 1) # Arredonda para 1 casa decimal
            })

        return Response({"data": response_data}, status=200)
    

class DetectionsByPeriodAPIView(APIView):
    """
    Endpoint 5.2: Detecções por Período (Gráfico de Linha)
    Agrupa detecções por 'hour', 'day', 'week' ou 'month'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        period = request.query_params.get('period', 'day') # Padrão: dia

        # 1. Mapeamento de Funções de Agregação
        # Mapeia o parâmetro 'period' para a função de agregação do Django
        period_map = {
            'hour': 'hour',
            'day': 'day',
            'week': 'week',
            'month': 'month',
        }
        
        if period not in period_map:
            return Response({"error": "Parâmetro 'period' inválido."}, status=400)

        # 2. Filtra detecções APENAS das câmeras do usuário.
        detections_queryset = Deteccao.objects.filter(camera__owner=user)

        # 3. Agregação: Trunca o timestamp pelo período e conta
        data = detections_queryset.annotate(
            # Trunca o timestamp (ex: '2025-11-04 15:30:00' -> '2025-11-04 00:00:00')
            period_label=Trunc('timestamp', period_map[period]) 
        ).values('period_label').annotate(
            count=Count('id')
        ).order_by('period_label')

        # 4. Formata a resposta
        response_data = [
            {
                # O formato do Django é um objeto datetime,
                # precisamos formatá-lo para a resposta da API.
                "date": item['period_label'].isoformat(),
                "count": item['count']
            }
            for item in data
        ]

        return Response({"period": period, "data": response_data}, status=200)