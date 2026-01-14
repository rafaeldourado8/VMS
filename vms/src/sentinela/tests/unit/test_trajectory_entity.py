import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain.entities.trajectory import Trajectory
from domain.entities.trajectory_point import TrajectoryPoint

def test_trajectory_creation():
    points = [
        TrajectoryPoint('cam1', 'Camera 1', datetime.now(), '/img1.jpg', 0.95),
        TrajectoryPoint('cam2', 'Camera 2', datetime.now(), '/img2.jpg', 0.85)
    ]
    
    trajectory = Trajectory(search_id='search-1', points=points)
    
    assert trajectory.search_id == 'search-1'
    assert len(trajectory.points) == 2

def test_trajectory_get_timeline():
    now = datetime.now()
    points = [
        TrajectoryPoint('cam2', 'Camera 2', now + timedelta(minutes=5), '/img2.jpg', 0.85),
        TrajectoryPoint('cam1', 'Camera 1', now, '/img1.jpg', 0.95),
        TrajectoryPoint('cam3', 'Camera 3', now + timedelta(minutes=10), '/img3.jpg', 0.90)
    ]
    
    trajectory = Trajectory(search_id='search-1', points=points)
    timeline = trajectory.get_timeline()
    
    assert len(timeline) == 3
    assert timeline[0].camera_id == 'cam1'  # Primeiro no tempo
    assert timeline[1].camera_id == 'cam2'
    assert timeline[2].camera_id == 'cam3'  # Último no tempo

def test_trajectory_get_cameras_visited():
    points = [
        TrajectoryPoint('cam1', 'Camera 1', datetime.now(), '/img1.jpg', 0.95),
        TrajectoryPoint('cam2', 'Camera 2', datetime.now(), '/img2.jpg', 0.85),
        TrajectoryPoint('cam1', 'Camera 1', datetime.now(), '/img3.jpg', 0.90)  # Repetida
    ]
    
    trajectory = Trajectory(search_id='search-1', points=points)
    cameras = trajectory.get_cameras_visited()
    
    assert len(cameras) == 2  # cam1 e cam2 (sem duplicatas)
    assert 'cam1' in cameras
    assert 'cam2' in cameras

def test_trajectory_get_total_detections():
    points = [
        TrajectoryPoint('cam1', 'Camera 1', datetime.now(), '/img1.jpg', 0.95),
        TrajectoryPoint('cam2', 'Camera 2', datetime.now(), '/img2.jpg', 0.85)
    ]
    
    trajectory = Trajectory(search_id='search-1', points=points)
    
    assert trajectory.get_total_detections() == 2

def test_trajectory_get_high_confidence_points():
    points = [
        TrajectoryPoint('cam1', 'Camera 1', datetime.now(), '/img1.jpg', 0.95),  # High
        TrajectoryPoint('cam2', 'Camera 2', datetime.now(), '/img2.jpg', 0.85),  # Low
        TrajectoryPoint('cam3', 'Camera 3', datetime.now(), '/img3.jpg', 0.92)   # High
    ]
    
    trajectory = Trajectory(search_id='search-1', points=points)
    high_conf = trajectory.get_high_confidence_points()
    
    assert len(high_conf) == 2
    assert all(p.confidence >= 0.9 for p in high_conf)
