@echo off
echo Aplicando campos de localizacao diretamente no banco...
echo.

docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS address_street VARCHAR(255);"
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS address_number VARCHAR(20);"
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS address_neighborhood VARCHAR(100);"
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS address_city VARCHAR(100);"
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS address_state VARCHAR(2);"
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "ALTER TABLE cameras_camera ADD COLUMN IF NOT EXISTS maps_url VARCHAR(1000);"

echo.
echo Campos adicionados com sucesso!
echo Reiniciando backend...
docker-compose restart backend

echo.
echo Concluido!
pause
