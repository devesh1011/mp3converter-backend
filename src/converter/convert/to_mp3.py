import pika
import json
import tempfile
from bson.objectid import ObjectId
from moviepy import VideoFileClip
import os


def start(msg, fs_videos, fs_mp3s, channel):
    try:
        # Decode bytes to string if necessary
        if isinstance(msg, bytes):
            msg = msg.decode("utf-8")
        message = json.loads(msg)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"success": False, "error": f"invalid json: {e}"}

    video_fid = message.get("video_fid")
    if not video_fid:
        return {"success": False, "error": "missing video_fid"}

    # Create temp video file
    tf = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    temp_video_path = tf.name

    try:
        out = fs_videos.get(ObjectId(video_fid))
        tf.write(out.read())
        tf.flush()
    finally:
        tf.close()

    # Extract audio from video
    try:
        clip = VideoFileClip(temp_video_path)
        audio = clip.audio

        temp_audio_path = os.path.join(tempfile.gettempdir(), f"{video_fid}.mp3")
        audio.write_audiofile(temp_audio_path)
        clip.close()
    except Exception as err:
        os.remove(temp_video_path)
        return {"success": False, "error": f"audio extraction failed: {err}"}

    # Store audio in GridFS
    try:
        with open(temp_audio_path, "rb") as f:
            mp3_fid = fs_mp3s.put(f.read())
    except Exception as err:
        os.remove(temp_video_path)
        os.remove(temp_audio_path)
        return {"success": False, "error": f"gridfs write failed: {err}"}

    # Clean up temp files
    os.remove(temp_video_path)
    os.remove(temp_audio_path)

    # Publish message with mp3_fid
    message["mp3_fid"] = str(mp3_fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception:
        fs_mp3s.delete(mp3_fid)
        return {"success": False, "error": "failed to publish message"}

    return {"success": True, "mp3_fid": str(mp3_fid)}
