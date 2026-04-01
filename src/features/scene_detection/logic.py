"""Logic for the scene detection feature using PySceneDetect."""

import os
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from .models import Scene


def detect_scenes(video_path: str) -> list[Scene]:
    """
    Detect visual scene boundaries in a video file.

    Uses PySceneDetect's ContentDetector with a default threshold of 27.0.
    If no cuts are detected, returns a single scene covering the full duration.

    Args:
        video_path: Path to the video file.

    Returns:
        List of Scene objects with 1-based scene numbers and start/end in ms.

    Raises:
        FileNotFoundError: If the video file does not exist.
        ValueError: If the video file cannot be read.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=27.0))
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Could not read video file: {str(e)}")

    if not scene_list:
        total_ms = int(video.duration.get_seconds() * 1000)
        return [Scene(scene_number=1, start_ms=0, end_ms=total_ms)]

    return [
        Scene(
            scene_number=i + 1,
            start_ms=int(start.get_seconds() * 1000),
            end_ms=int(end.get_seconds() * 1000),
        )
        for i, (start, end) in enumerate(scene_list)
    ]
