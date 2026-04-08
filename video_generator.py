"""
Book2Audio 视频处理模块
"""
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
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
            os.environ["PATH"] += os.pathsep + ffmpeg_dir

    def generate_video(self, audio_file: str, subtitle_file: str,
                      background_image: str, output_video: str) -> bool:
        """生成带字幕的视频"""
        self._setup_environment()

        # 检查文件是否存在
        if not os.path.exists(audio_file):
            logger.error(f"音频文件不存在: {audio_file}")
            return False

        if not os.path.exists(subtitle_file):
            logger.error(f"字幕文件不存在: {subtitle_file}")
            return False

        if not os.path.exists(background_image):
            logger.error(f"背景图片不存在: {background_image}")
            return False

        ensure_dir(os.path.dirname(output_video))

        try:
            logger.info("开始生成视频...")

            # 使用正斜杠并转义路径
            audio_path = audio_file.replace('\\', '/')
            subtitle_path = subtitle_file.replace('\\', '/')
            background_path = background_image.replace('\\', '/')
            output_path = output_video.replace('\\', '/')

            # 构建 FFmpeg 命令
            cmd = [
                self.ffmpeg_path,
                "-loop", "1",  # 循环背景图片
                "-i", background_path,  # 背景图片输入
                "-i", audio_path,  # 音频输入
                "-vf", ",".join([
                    f"scale={self.video_width}:{self.video_height}:force_original_aspect_ratio=decrease",
                    "pad={}:{}:(ow-iw)/2:(oh-ih)/2".format(self.video_width, self.video_height),
                    f"subtitles='{subtitle_path}':force_style='FontSize={self.font_size},PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1'"
                ]),
                "-c:v", "libx264",  # 视频编码器
                "-c:a", "aac",  # 音频编码器
                "-shortest",  # 以最短流结束
                "-y",  # 覆盖输出文件
                output_path
            ]

            logger.debug(f"FFmpeg 命令: {' '.join(cmd)}")

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode == 0:
                logger.info(f"视频生成成功: {output_video}")
                return True
            else:
                logger.error(f"视频生成失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"视频生成异常: {e}")
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
                logger.error(f"获取视频信息失败: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"获取视频信息异常: {e}")
            return None</content>
<parameter name="filePath">d:\book2audio\video_generator.py