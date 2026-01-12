from prometheus_client import Counter, Gauge, Histogram

# Active streams gauge
vms_streams_active = Gauge(
    'vms_streams_active',
    'Number of active streams',
    ['camera_id']
)

# Stream errors counter
vms_stream_errors_total = Counter(
    'vms_stream_errors_total',
    'Total stream errors',
    ['camera_id', 'error_type']
)

# Reconnect duration histogram
vms_reconnect_duration_seconds = Histogram(
    'vms_reconnect_duration_seconds',
    'Time taken to reconnect stream',
    ['camera_id'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)
