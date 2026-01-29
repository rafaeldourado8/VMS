@echo off
timeout /t 10 /nobreak
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':555,'rtsp_url':'/app/test_video.mp4'}));print('Camera publicada')"
timeout /t 5 /nobreak
docker-compose logs --tail=50 lpr_service
