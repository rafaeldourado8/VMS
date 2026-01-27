
@app.post("/api/mosaics/create")
async def create_mosaic(
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    mosaic = await sync_to_async(mosaic_manager.create_mosaic)(x_city_id, x_user_id)
    return mosaic.to_dict()

@app.get("/api/mosaics/{mosaic_id}")
async def get_mosaic(
    mosaic_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    mosaic = await sync_to_async(mosaic_manager.get_mosaic)(mosaic_id, x_city_id)
    if not mosaic:
        raise HTTPException(status_code=404, detail="Mosaic not found")
    return mosaic.to_dict()

@app.post("/api/mosaics/{mosaic_id}/add/{session_id}")
async def add_stream_to_mosaic(
    mosaic_id: str,
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    added = await sync_to_async(mosaic_manager.add_stream_to_mosaic)(mosaic_id, session_id, x_city_id)
    if not added:
        raise HTTPException(status_code=400, detail="Cannot add stream (max 4 or mosaic not found)")
    return {"status": "added"}

@app.delete("/api/mosaics/{mosaic_id}/remove/{session_id}")
async def remove_stream_from_mosaic(
    mosaic_id: str,
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    removed = await sync_to_async(mosaic_manager.remove_stream_from_mosaic)(mosaic_id, session_id, x_city_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Stream or mosaic not found")
    return {"status": "removed"}

@app.delete("/api/mosaics/{mosaic_id}")
async def delete_mosaic(
    mosaic_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    deleted = await sync_to_async(mosaic_manager.delete_mosaic)(mosaic_id, x_city_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mosaic not found")
    return {"status": "deleted"}
