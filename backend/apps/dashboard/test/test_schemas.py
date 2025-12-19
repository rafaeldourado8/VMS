from apps.dashboard.schemas import DashboardStatsDTO

def test_dashboard_stats_dto_structure():
    dto = DashboardStatsDTO(
        total_cameras=10, cameras_online=8, cameras_offline=2,
        total_detections_24h=50, detections_by_type={"car": 40}, recent_activity=[]
    )
    assert dto.total_cameras == 10
    assert dto.cameras_online == 8