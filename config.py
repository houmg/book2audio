"""
Book2Audio 配置管理模块
"""
import configparser
from pathlib import Path


class Config:
    """配置管理类"""

    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.RawConfigParser()

        # 默认配置
        self.defaults = {
            'input_file': 'input.txt',
            'output_dir': 'output',
            'voice': 'zh-CN-XiaoxiaoNeural',
            'rate': '+0%',
            'volume': '+0%',
            'pitch': '+0Hz',
            'segment_size': '500',
            'video_width': '1920',
            'video_height': '1080',
            'font_size': '48',
            'ffmpeg_path': '',
            'ffprobe_path': ''
        }

        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        if self.config_file.exists():
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 创建默认配置
            self.config['DEFAULT'] = self.defaults
            self.save_config()

    def save_config(self) -> None:
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get(self, key: str, default: str = None) -> str:
        """获取配置值"""
        if default is None:
            default = self.defaults.get(key, '')
        return self.config.get('DEFAULT', key, fallback=default)

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值"""
        try:
            return self.config.getint('DEFAULT', key, fallback=default)
        except ValueError:
            return default

    def set(self, key: str, value: str) -> None:
        """设置配置值"""
        if not self.config.has_section('DEFAULT'):
            self.config.add_section('DEFAULT')
        self.config.set('DEFAULT', key, value)
        self.save_config()

    @property
    def input_file(self) -> str:
        return self.get('input_file')

    @property
    def output_dir(self) -> str:
        return self.get('output_dir')

    @property
    def voice(self) -> str:
        return self.get('voice')

    @property
    def rate(self) -> str:
        return self.get('rate')

    @property
    def volume(self) -> str:
        return self.get('volume')

    @property
    def pitch(self) -> str:
        return self.get('pitch')

    @property
    def segment_size(self) -> int:
        return self.get_int('segment_size', 500)

    @property
    def video_width(self) -> int:
        return self.get_int('video_width', 1920)

    @property
    def video_height(self) -> int:
        return self.get_int('video_height', 1080)

    @property
    def font_size(self) -> int:
        return self.get_int('font_size', 48)

    @property
    def ffmpeg_path(self) -> str:
        return self.get('ffmpeg_path')

    @property
    def ffprobe_path(self) -> str:
        return self.get('ffprobe_path')


# 全局配置实例
config = Config()