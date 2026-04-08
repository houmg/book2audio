"""
Book2Audio 音频处理模块
"""
import os
import glob
import re
from pathlib import Path
from typing import List, Tuple, Optional

from pydub import AudioSegment
from .config import config
from .logger import logger
from .utils import ensure_dir, get_file_list, format_time_srt, parse_srt_time


class AudioProcessor:
    """音频处理器类"""

    def __init__(self):
        self._setup_ffmpeg()

    def _setup_ffmpeg(self):
        """设置 FFmpeg 路径"""
        ffmpeg_path = config.ffmpeg_path
        ffprobe_path = config.ffprobe_path

        if ffmpeg_path and os.path.exists(ffmpeg_path):
            AudioSegment.converter = ffmpeg_path
            os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

        if ffprobe_path and os.path.exists(ffprobe_path):
            AudioSegment.ffprobe = ffprobe_path
            os.environ["PATH"] += os.pathsep + os.path.dirname(ffprobe_path)

    def get_audio_files(self, input_dir: str) -> List[Path]:
        """获取排序后的音频文件列表"""
        return sorted(get_file_list(input_dir, "part_*.mp3"))

    def get_subtitle_files(self, input_dir: str) -> List[Path]:
        """获取排序后的字幕文件列表"""
        return sorted(get_file_list(input_dir, "part_*.srt"))

    def merge_audio_files(self, audio_files: List[Path], output_path: Path) -> bool:
        """合并音频文件"""
        if not audio_files:
            logger.error("没有找到音频文件")
            return False

        try:
            logger.info(f"合并 {len(audio_files)} 个音频文件...")

            # 加载第一个音频文件
            combined = AudioSegment.from_mp3(str(audio_files[0]))

            # 依次添加其他文件
            for audio_file in audio_files[1:]:
                audio = AudioSegment.from_mp3(str(audio_file))
                combined += audio

            # 导出合并后的音频
            combined.export(str(output_path), format="mp3")
            logger.info(f"音频合并完成: {output_path}")
            return True

        except Exception as e:
            logger.error(f"音频合并失败: {e}")
            return False

    def merge_subtitles(self, subtitle_files: List[Path], output_path: Path) -> bool:
        """合并字幕文件"""
        if not subtitle_files:
            logger.error("没有找到字幕文件")
            return False

        try:
            logger.info(f"合并 {len(subtitle_files)} 个字幕文件...")

            merged_content = []
            global_index = 1
            time_offset = 0.0

            for srt_file in subtitle_files:
                with open(srt_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()

                # 解析 SRT 内容
                blocks = re.split(r'\n\s*\n', content.strip())
                audio_duration = self._get_audio_duration_from_srt(blocks)

                for block in blocks:
                    lines = block.strip().split('\n')
                    if len(lines) >= 3:
                        # 解析时间戳
                        time_line = lines[1]
                        if '-->' in time_line:
                            start_time, end_time = time_line.split('-->')
                            start_seconds = parse_srt_time(start_time.strip()) + time_offset
                            end_seconds = parse_srt_time(end_time.strip()) + time_offset

                            # 写入新的字幕块
                            merged_content.append(str(global_index))
                            merged_content.append(f"{format_time_srt(start_seconds)} --> {format_time_srt(end_seconds)}")
                            merged_content.extend(lines[2:])  # 字幕文本
                            merged_content.append("")  # 空行

                            global_index += 1

                time_offset += audio_duration

            # 写入合并后的字幕文件
            with open(output_path, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(merged_content))

            logger.info(f"字幕合并完成: {output_path}")
            return True

        except Exception as e:
            logger.error(f"字幕合并失败: {e}")
            return False

    def _get_audio_duration_from_srt(self, srt_blocks: List[str]) -> float:
        """从 SRT 块估算音频时长"""
        if not srt_blocks:
            return 0.0

        # 获取最后一个字幕块的结束时间
        last_block = srt_blocks[-1]
        lines = last_block.strip().split('\n')
        if len(lines) >= 2 and '-->' in lines[1]:
            _, end_time = lines[1].split('-->')
            return parse_srt_time(end_time.strip())

        return 0.0

    def merge_audio_and_subtitles(self, input_dir: str, output_audio: str, output_subtitle: str) -> bool:
        """合并音频和字幕文件"""
        ensure_dir(os.path.dirname(output_audio))
        ensure_dir(os.path.dirname(output_subtitle))

        audio_files = self.get_audio_files(input_dir)
        subtitle_files = self.get_subtitle_files(input_dir)

        if len(audio_files) != len(subtitle_files):
            logger.warning(f"音频文件数量 ({len(audio_files)}) 与字幕文件数量 ({len(subtitle_files)}) 不匹配")

        success = True

        if audio_files:
            success &= self.merge_audio_files(audio_files, Path(output_audio))

        if subtitle_files:
            success &= self.merge_subtitles(subtitle_files, Path(output_subtitle))

        return success</content>
<parameter name="filePath">d:\book2audio\audio_processor.py