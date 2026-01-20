from flask import Flask, request, jsonify
import logging
from threading import Thread

class ControlAPI:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.port = port
        self.active_cameras = {}
        self.logger = logging.getLogger(__name__)
        
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'ok',
                'active_cameras': len(self.active_cameras)
            }), 200
        
        @self.app.route('/cameras/<int:camera_id>/start', methods=['POST'])
        def start_camera(camera_id):
            data = request.json or {}
            source_url = data.get('source_url')  # Opcional
            
            if camera_id in self.active_cameras:
                return jsonify({'error': 'camera already active'}), 400
            
            # Callback será definido externamente
            if hasattr(self, 'start_camera_callback'):
                success = self.start_camera_callback(camera_id, source_url)
                if success:
                    self.active_cameras[camera_id] = source_url or f"mediamtx://cam_{camera_id}"
                    return jsonify({
                        'status': 'started',
                        'camera_id': camera_id
                    }), 200
            
            return jsonify({'error': 'failed to start camera'}), 500
        
        @self.app.route('/cameras/<int:camera_id>/stop', methods=['POST'])
        def stop_camera(camera_id):
            
            if camera_id not in self.active_cameras:
                return jsonify({'error': 'camera not active'}), 404
            
            if hasattr(self, 'stop_camera_callback'):
                success = self.stop_camera_callback(camera_id)
                if success:
                    del self.active_cameras[camera_id]
                    return jsonify({
                        'status': 'stopped',
                        'camera_id': camera_id
                    }), 200
            
            return jsonify({'error': 'failed to stop camera'}), 500
        
        @self.app.route('/cameras', methods=['GET'])
        def list_cameras():
            return jsonify({
                'cameras': [
                    {'id': cid, 'url': url}
                    for cid, url in self.active_cameras.items()
                ]
            }), 200
    
    def set_callbacks(self, start_callback, stop_callback):
        self.start_camera_callback = start_callback
        self.stop_camera_callback = stop_callback
    
    def run(self):
        thread = Thread(
            target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False),
            daemon=True
        )
        thread.start()
        self.logger.info(f"Control API started on port {self.port}")
        return thread
