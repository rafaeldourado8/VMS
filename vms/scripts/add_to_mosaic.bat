@echo off
set CITY_ID=2ca65fec-ed93-40d1-bdf2-386a94e25fb1
set MOSAIC_ID=mosaic_c11cde01-e82a-48cc-936c-37d9bae57470

echo === Adicionando streams ao mosaico ===
echo.

curl -X POST http://localhost:8001/api/mosaics/%MOSAIC_ID%/add/stream_d7ebdaac-9d09-470f-a208-34ce2e4f9689 -H "X-City-ID: %CITY_ID%"
echo.

curl -X POST http://localhost:8001/api/mosaics/%MOSAIC_ID%/add/stream_7cca767f-c25d-478a-9534-2a04f976b2a8 -H "X-City-ID: %CITY_ID%"
echo.

curl -X POST http://localhost:8001/api/mosaics/%MOSAIC_ID%/add/stream_59227f16-4e81-4348-9916-9e2a96329acb -H "X-City-ID: %CITY_ID%"
echo.

curl -X POST http://localhost:8001/api/mosaics/%MOSAIC_ID%/add/stream_63a5c1a2-5e5f-43c1-b382-33dc6d5ad287 -H "X-City-ID: %CITY_ID%"
echo.

echo === Verificando mosaico ===
curl http://localhost:8001/api/mosaics/%MOSAIC_ID% -H "X-City-ID: %CITY_ID%"
echo.
pause
