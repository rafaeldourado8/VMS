@echo off
set SESSION_ID=stream_8392ef0c-eac9-4dfc-a38a-e4cf4a114517
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1

echo Stopping stream...
curl -X POST http://localhost:8001/api/streaming/stop/%SESSION_ID% -H "X-City-ID: %CITY_ID%"

echo.
echo.
echo Checking MediaMTX paths...
curl http://localhost:9997/v3/paths/list

echo.
pause
