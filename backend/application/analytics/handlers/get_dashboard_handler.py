from ..queries.get_dashboard_query import GetDashboardQuery

from domain.analytics import Dashboard, Period, AnalyticsRepository, MetricsCalculator

class GetDashboardHandler:
    """Handler para buscar dados do dashboard"""
    
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository
        self.calculator = MetricsCalculator(repository)
    
    def handle(self, query: GetDashboardQuery) -> Dashboard:
        """Executa o use case de buscar dashboard"""
        
        # Determinar período
        if query.start_date and query.end_date:
            period = Period(query.start_date, query.end_date)
        elif query.period_type == "hour":
            period = Period.last_24_hours()
        elif query.period_type == "week":
            period = Period.last_7_days()
        elif query.period_type == "month":
            period = Period.last_30_days()
        else:  # day
            period = Period.last_24_hours()
        
        return self.calculator.calculate_dashboard_metrics(period)