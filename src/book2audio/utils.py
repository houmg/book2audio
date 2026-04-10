"""Book2Audio 工具模块"""
import re
from pathlib import Path
from typing import List


def ensure_dir(path: str) -> Path:
    """确保目录存在"""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def read_text_file(file_path: str, encodings: List[str] = None) -> str:
    """读取文本文件，支持多种编码"""
    if encodings is None:
        encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(f"无法读取文件：{file_path}")


def split_text_by_sentences(text: str, max_len: int = 500) -> List[str]:
    """按句子分割文本"""
    sentences = re.split(r'(?<=[.!?。！？.;])|(?<=\.{3})|(?<=\n)', text)

    segments = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        if len(current) + len(sent) <= max_len:
            current += sent
        else:
            if current:
                segments.append(current)
            if len(sent) > max_len:
                for i in range(0, len(sent), max_len):
                    segments.append(sent[i:i + max_len])
                current = ""
            else:
                current = sent

    if current:
        segments.append(current)

    return segments


def format_time_srt(seconds: float) -> str:
    """将秒转换为 SRT 时间格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_time_from_offset(offset: int) -> str:
    """将 100ns 单位的时间戳转换为 SRT 格式"""
    seconds = offset / 10_000_000
    return format_time_srt(seconds)


def parse_srt_time(time_str: str) -> float:
    """将 SRT 时间格式转换为秒"""
    hours, minutes, rest = time_str.split(':')
    seconds, millis = rest.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def get_file_list(directory: str, pattern: str = "*") -> List[Path]:
    """获取目录中的文件列表"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    return list(dir_path.glob(pattern))
