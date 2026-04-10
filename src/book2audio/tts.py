"""Book2Audio TTS 模块"""
import asyncio
import json
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional

from .config import config
from .logger import logger
from .utils import format_time_from_offset, ensure_dir


class TTSGenerator:
    """TTS 生成器类"""

    def __init__(self):
        self.voice = config.voice
        self.rate = config.rate
        self.volume = config.volume
        self.pitch = config.pitch

    def _parse_subtitle_json(self, content: str) -> List[Dict]:
        """解析字幕 JSON 内容"""
        subs = []
        for line in content.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict) and data.get('type') == 'SentenceBoundary':
                    start = data.get('offset')
                    duration = data.get('duration', 0)
                    if start is not None and data.get('text', ''):
                        subs.append({
                            'start': start,
                            'end': start + duration if start is not None else None,
                            'text': data.get('text', '')
                        })
            except json.JSONDecodeError:
                for match in re.findall(r'\{[^{}]*\}', line):
                    try:
                        data = json.loads(match)
                        if isinstance(data, dict) and data.get('type') == 'SentenceBoundary':
                            start = data.get('offset')
                            if start is not None and data.get('text', ''):
                                subs.append({
                                    'start': start,
                                    'end': start + data.get('duration', 0),
                                    'text': data.get('text', '')
                                })
                    except:
                        continue
        return subs

    async def generate_segment(self, text: str, audio_path: Path, srt_path: Path) -> int:
        """生成单个段落的音频和字幕"""
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False, encoding='utf-8') as tmp:
                tmp_sub_path = tmp.name

            cmd = [
                "edge-tts",
                "--text", text,
                "--write-media", str(audio_path),
                "--write-subtitles", tmp_sub_path,
                "--voice", self.voice,
                "--rate", self.rate,
                "--volume", self.volume,
                "--pitch", self.pitch
            ]

            logger.debug(f"执行命令：{' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "未知错误"
                logger.error(f"TTS 命令执行失败：{error_msg}")
                raise Exception(f"TTS 生成失败：{error_msg}")

            if os.path.exists(tmp_sub_path) and os.path.getsize(tmp_sub_path) > 0:
                with open(tmp_sub_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                subs = self._parse_subtitle_json(content)
                if subs:
                    with open(srt_path, 'w', encoding='utf-8-sig') as f:
                        for i, sub in enumerate(subs, 1):
                            f.write(f"{i}\n")
                            f.write(f"{format_time_from_offset(sub['start'])} --> {format_time_from_offset(sub['end'])}\n")
                            sub_text = re.sub(r'([.!?])', r'\1\n', sub['text'])
                            f.write(f"{sub_text}\n\n")
                    try:
                        os.remove(tmp_sub_path)
                    except:
                        pass
                    return len(subs)
                elif os.path.exists(tmp_sub_path):
                    shutil.move(tmp_sub_path, srt_path)
                    return 1

            try:
                if os.path.exists(tmp_sub_path):
                    os.remove(tmp_sub_path)
            except:
                pass

            return 0

        except asyncio.TimeoutError:
            raise Exception("TTS 生成超时")
        except Exception as e:
            logger.error(f"TTS 生成异常：{e}")
            raise

    async def generate_batch(self, segments: List[str], output_dir: Path,
                             progress_callback: Optional[callable] = None) -> int:
        """批量生成音频和字幕"""
        ensure_dir(output_dir)
        success_count = 0
        total = len(segments)

        for i, segment in enumerate(segments):
            audio_path = output_dir / f"part_{i + 1:04d}.mp3"
            srt_path = output_dir / f"part_{i + 1:04d}.srt"

            logger.info(f"[{i + 1}/{total}] 生成中... ({len(segment)}字)")
            start_time = time.time()

            try:
                sub_count = await self.generate_segment(segment, audio_path, srt_path)
                elapsed = time.time() - start_time

                if sub_count > 0:
                    logger.info(f"完成 ({elapsed:.1f}秒) - 字幕 {sub_count} 句")
                elif audio_path.exists() and audio_path.stat().st_size > 0:
                    logger.info(f"完成 ({elapsed:.1f}秒) - 音频已生成")
                else:
                    logger.warning("失败 - 未生成任何文件")
                    continue

                success_count += 1
                if progress_callback:
                    progress_callback(i + 1, total, success_count)

            except Exception as e:
                logger.error(f"失败：{e}")

            await asyncio.sleep(0.5)

        return success_count
