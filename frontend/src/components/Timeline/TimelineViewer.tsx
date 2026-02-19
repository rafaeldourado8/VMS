import React, { useState, useEffect, useRef } from 'react';
import { format, startOfDay, addDays, subDays } from 'date-fns';
import './TimelineViewer.css';

interface TimelineBlock {
  start_time: string;
  end_time: string;
  duration: number;
  file_path: string;
  file_size: number;
}

interface TimelineViewerProps {
  cameraId: string;
  selectedDate: Date;
  onVideoSelect: (filePath: string, timestamp: string) => void;
}

export const TimelineViewer: React.FC<TimelineViewerProps> = ({
  cameraId,
  selectedDate,
  onVideoSelect
}) => {
  const [timeline, setTimeline] = useState<TimelineBlock[]>([]);
  const [loading, setLoading] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const timelineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadTimeline();
  }, [cameraId, selectedDate]);

  const loadTimeline = async () => {
    setLoading(true);
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      const response = await fetch(`/api/timeline/${cameraId}?date=${dateStr}`);
      const data = await response.json();
      setTimeline(data.blocks || []);
    } catch (error) {
      console.error('Error loading timeline:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockClick = (block: TimelineBlock, clickX: number) => {
    const blockElement = document.querySelector(`[data-block="${block.start_time}"]`) as HTMLElement;
    if (!blockElement) return;

    const rect = blockElement.getBoundingClientRect();
    const relativeX = clickX - rect.left;
    const percentage = relativeX / rect.width;
    
    const startTime = new Date(block.start_time);
    const endTime = new Date(block.end_time);
    const duration = endTime.getTime() - startTime.getTime();
    const targetTime = new Date(startTime.getTime() + (duration * percentage));
    
    // Converter MP4 path para HLS URL
    const hlsUrl = `${block.file_path}/index.m3u8`;
    onVideoSelect(hlsUrl, targetTime.toISOString());
  };

  const renderTimelineBlocks = () => {
    const dayStart = startOfDay(selectedDate);
    const dayEnd = addDays(dayStart, 1);
    const totalMinutes = 24 * 60;

    return (
      <div className="timeline-blocks" style={{ transform: `scaleX(${zoomLevel})` }}>
        {timeline.map((block, index) => {
          const startTime = new Date(block.start_time);
          const endTime = new Date(block.end_time);
          
          const startMinutes = (startTime.getTime() - dayStart.getTime()) / (1000 * 60);
          const duration = (endTime.getTime() - startTime.getTime()) / (1000 * 60);
          
          const left = (startMinutes / totalMinutes) * 100;
          const width = (duration / totalMinutes) * 100;

          return (
            <div
              key={index}
              className="timeline-block"
              data-block={block.start_time}
              style={{
                left: `${left}%`,
                width: `${width}%`,
              }}
              onClick={(e) => handleBlockClick(block, e.clientX)}
              title={`${format(startTime, 'HH:mm:ss')} - ${format(endTime, 'HH:mm:ss')}`}
            />
          );
        })}
      </div>
    );
  };

  const renderTimeMarkers = () => {
    const markers = [];
    for (let hour = 0; hour < 24; hour++) {
      const left = (hour / 24) * 100;
      markers.push(
        <div key={hour} className="time-marker" style={{ left: `${left}%` }}>
          <span>{hour.toString().padStart(2, '0')}:00</span>
        </div>
      );
    }
    return markers;
  };

  return (
    <div className="timeline-viewer">
      <div className="timeline-header">
        <div className="date-navigation">
          <button onClick={() => onVideoSelect('', subDays(selectedDate, 1).toISOString())}>
            ← Previous Day
          </button>
          <span className="current-date">{format(selectedDate, 'dd/MM/yyyy')}</span>
          <button onClick={() => onVideoSelect('', addDays(selectedDate, 1).toISOString())}>
            Next Day →
          </button>
        </div>
        <div className="zoom-controls">
          <button onClick={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.5))}>Zoom Out</button>
          <span>{zoomLevel}x</span>
          <button onClick={() => setZoomLevel(Math.min(4, zoomLevel + 0.5))}>Zoom In</button>
        </div>
      </div>

      <div className="timeline-container" ref={timelineRef}>
        <div className="time-markers">
          {renderTimeMarkers()}
        </div>
        {loading ? (
          <div className="timeline-loading">Loading timeline...</div>
        ) : (
          renderTimelineBlocks()
        )}
      </div>

      <div className="timeline-info">
        <span>Recordings: {timeline.length}</span>
        <span>Total Duration: {Math.round(timeline.reduce((sum, block) => sum + block.duration, 0) / 60)} minutes</span>
      </div>
    </div>
  );
};