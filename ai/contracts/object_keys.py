def original_object_key(video_id: str) -> str:
    return f"videos/{video_id}/original.mp4"


def clip_object_key(video_id: str, start_ms: int, end_ms: int) -> str:
    return f"clips/{video_id}/{start_ms}-{end_ms}-h264_720p.mp4"
