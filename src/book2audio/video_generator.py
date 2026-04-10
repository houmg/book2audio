"""Book2Audio 视频处理模块"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .config import config
from .logger import logger
from .utils import ensure_dir


class VideoGenerator:
    """视频生成器类"""

    def __init__(self):
        self.ffmpeg_path = config.ffmpeg_path or shutil.which("ffmpeg")
        self.ffprobe_path = config.ffprobe_path or shutil.which("ffprobe")
        self.video_width = config.video_width
        self.video_height = config.video_height
        self.font_size = config.font_size

        if not self.ffmpeg_path:
            raise RuntimeError("未找到 ffmpeg，请在 config.ini 中设置 ffmpeg_path")

    def _setup_environment(self):
        """设置环境变量"""
        if self.ffmpeg_path:
            os.environ["PATH"] += os.pathsep + os.path.dirname(self.ffmpeg_path)

    def generate_video(self, audio_file: str, subtitle_file: str,
                       background_image: str, output_video: str) -> bool:
        """生成带字幕的视频"""
        self._setup_environment()

        for file_path, file_type in [(audio_file, "音频"), (subtitle_file, "字幕"), (background_image, "背景图片")]:
            if not os.path.exists(file_path):
                logger.error(f"{file_type}文件不存在：{file_path}")
                return False

        ensure_dir(os.path.dirname(output_video))

        try:
            logger.info("开始生成视频...")

            cmd = [
                self.ffmpeg_path,
                "-loop", "1",
                "-i", background_image.replace('\\', '/'),
                "-i", audio_file.replace('\\', '/'),
                "-vf", ",".join([
                    f"scale={self.video_width}:{self.video_height}:force_original_aspect_ratio=decrease",
                    f"pad={self.video_width}:{self.video_height}:(ow-iw)/2:(oh-ih)/2",
                    f"subtitles='{subtitle_file.replace(chr(92), '/')}':force_style='FontSize={self.font_size},PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1'"
                ]),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                "-y",
                output_video.replace('\\', '/')
            ]

            logger.debug(f"FFmpeg 命令：{' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

            if result.returncode == 0:
                logger.info(f"视频生成成功：{output_video}")
                return True
            else:
                logger.error(f"视频生成失败：{result.stderr}")
                return False

        except Exception as e:
            logger.error(f"视频生成异常：{e}")
            return False

    def get_video_info(self, video_file: str) -> Optional[dict]:
        """获取视频信息"""
        if not os.path.exists(video_file):
            return None

        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.error(f"获取视频信息失败：{result.stderr}")
                return None

        except Exception as e:
            logger.error(f"获取视频信息异常：{e}")
            return None
