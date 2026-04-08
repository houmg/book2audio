"""
Book2Audio - 将电子书转换为音频和视频

这是一个完整的电子书转换工具，支持多种格式的电子书，
使用 Microsoft Edge TTS 生成高质量音频，并可创建带字幕的视频。
"""

__version__ = "2.0.0"
__author__ = "Book2Audio Team"

from .cli import main
