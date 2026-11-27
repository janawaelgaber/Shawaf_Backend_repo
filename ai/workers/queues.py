PIPELINE_GPU = "pipeline.gpu"
PIPELINE_CPU = "pipeline.cpu"
MEDIA_CLIPS = "media.clips"
CALLBACKS = "callbacks"

QUEUES = (PIPELINE_GPU, PIPELINE_CPU, MEDIA_CLIPS, CALLBACKS)

def processing_queue(*, gpu_available: bool) -> str:
    if gpu_available:
        return PIPELINE_GPU

    return PIPELINE_CPU