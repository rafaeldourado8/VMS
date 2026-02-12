@echo off
echo Desabilitando gravacao no MediaMTX...

docker exec gtvision_mediamtx wget -qO- --post-data="{\"record\":false}" --header="Content-Type: application/json" http://localhost:9997/v3/config/pathdefaults/patch

echo.
echo Verificando paths ativos...
docker exec gtvision_mediamtx wget -qO- http://localhost:9997/v3/paths/list

echo.
echo Concluido!
pause
