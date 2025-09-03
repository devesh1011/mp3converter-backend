import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pymongo import MongoClient
import gridfs
import pika
from bson.objectid import ObjectId
from auth.validate import token
from storage import util
from auth_svc import access


app = FastAPI()

# Global connection (lazy initialized)
_rabbitmq_connection = None
_rabbitmq_channel = None


def get_rabbitmq_channel():
    """Lazy initialize RabbitMQ connection."""
    global _rabbitmq_connection, _rabbitmq_channel
    if _rabbitmq_channel is None or _rabbitmq_channel.is_closed:
        try:
            _rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", heartbeat=600)
            )
            _rabbitmq_channel = _rabbitmq_connection.channel()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to RabbitMQ: {e}")
    return _rabbitmq_channel


# Mongo connections
mongo_video = MongoClient(
    os.environ.get("MONGO_URI", "mongodb://host.minikube.internal:27017/videos")
)
mongo_mp3 = MongoClient(
    os.environ.get("MONGO_MP3_URI", "mongodb://host.minikube.internal:27017/mp3s")
)

fs_videos = gridfs.GridFS(mongo_video.videos)
fs_mp3s = gridfs.GridFS(mongo_mp3.mp3s)


@app.post("/login")
async def login(request: Request):
    token_result, err = access.login(request)

    if err:
        raise HTTPException(status_code=401, detail=err[0])

    return {"token": token_result}


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    access_token, err = token(request)

    if err:
        raise HTTPException(status_code=401, detail=err[0])

    access_data = access_token

    # if not access_data.get("admin"):
    #    raise HTTPException(status_code=403, detail="not authorized")

    try:
        channel = get_rabbitmq_channel()
        err = util.upload(file, fs_videos, channel, access_data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if err:
        raise HTTPException(status_code=400, detail=err)

    return JSONResponse({"status": "success"}, status_code=201)


@app.get("/download")
async def download(request: Request, fid: str):
    access_token, err = token(request)

    if err:
        raise HTTPException(status_code=401, detail=err[0])

    access_data = access_token

    # if not access_data.get("admin"):
    #    raise HTTPException(status_code=403, detail="not authorized")

    if not fid:
        raise HTTPException(status_code=400, detail="fid is required")

    try:
        out = fs_mp3s.get(ObjectId(fid))
        # Read the entire file content
        file_content = out.read()
        # Return as streaming response
        return StreamingResponse(
            iter([file_content]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={fid}.mp3"},
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
