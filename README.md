# Book2Audio

一个将电子书转换为音频和视频的项目，支持多种电子书格式（EPUB, MOBI, AZW3, PDF, TXT），使用 Microsoft Edge TTS 生成高质量音频，并可创建带字幕的视频。

## ✨ 新版本特性 (v2.0)

- 🏗️ **模块化架构**：代码重构为模块化设计，提高可维护性
- ⚙️ **配置管理**：支持配置文件和命令行参数
- 📝 **日志系统**：完整的日志记录和错误处理
- 🖥️ **命令行界面**：用户友好的CLI工具
- 🔧 **类型提示**：完整的类型注解
- 📦 **包管理**：支持 pip 安装和分发

## 功能特性

- **多格式支持**：支持 EPUB, MOBI, AZW3, PDF, TXT 等电子书格式
- **高质量TTS**：使用 Microsoft Edge TTS 生成自然流畅的中文语音
- **智能分段**：自动按句子分割文本，避免单次合成过长
- **字幕生成**：自动生成 SRT 字幕文件，与音频同步
- **音频合并**：将多个音频片段合并为完整音频文件
- **视频创建**：从音频、字幕和背景图片生成 MP4 视频
- **并行处理**：支持并发TTS生成，提高效率
- **错误恢复**：完善的错误处理和恢复机制

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/book2audio.git
cd book2audio

# 安装依赖
pip install -r requirements.txt

# 或安装为包
pip install -e .
```

### 基本使用

```bash
# 生成 TTS 音频和字幕
book2audio tts input.txt

# 合并音频和字幕
book2audio merge output/ book.mp3 book.srt

# 生成视频
book2audio video book.mp3 book.srt background.jpg output.mp4

# 完整流程（一键转换）
book2audio all input.txt background.jpg output.mp4
```

## 项目结构

```
book2audio/
├── __init__.py              # 包初始化
├── __main__.py              # 主入口
├── cli.py                   # 命令行接口
├── config.py                # 配置管理
├── logger.py                # 日志系统
├── utils.py                 # 工具函数
├── tts.py                   # TTS 生成器
├── audio_processor.py       # 音频处理
├── video_generator.py       # 视频生成器
├── extract_text.py          # 文本提取器
├── config.ini               # 配置文件模板
├── requirements.txt         # 依赖列表
├── setup.py                 # 包安装配置
├── Makefile                 # 构建脚本
└── README.md               # 文档
```

## 安装依赖

### Python 依赖

```bash
pip install edge-tts EbookLib mobi PyMuPDF pressor pydub
```

### 系统依赖

1. **FFmpeg**：用于音频处理和视频创建
   - 下载地址：https://www.gyan.dev/ffmpeg/builds/
   - 安装后确保 `ffmpeg.exe` 和 `ffprobe.exe` 在系统 PATH 中，或在代码中指定绝对路径

2. **字体**：确保系统安装了中文字体（如微软雅黑、宋体等）

## 配置

复制 `config.ini` 为你的配置文件，并根据需要修改参数：

```ini
[DEFAULT]
input_file = input.txt
output_dir = output
voice = zh-CN-XiaoxiaoNeural
rate = +0%
volume = +0%
pitch = +0Hz
segment_size = 500
video_width = 1920
video_height = 1080
font_size = 48
ffmpeg_path = C:\path\to\ffmpeg.exe
ffprobe_path = C:\path\to\ffprobe.exe
```

## 使用方法

### 命令行界面

Book2Audio 提供了完整的命令行界面：

```bash
# 显示帮助
book2audio --help

# 生成 TTS 音频和字幕
book2audio tts input.txt --voice zh-CN-YunxiNeural --rate +10%

# 合并音频和字幕
book2audio merge output/ merged.mp3 merged.srt

# 生成视频
book2audio video merged.mp3 merged.srt background.jpg output.mp4

# 完整转换流程
book2audio all novel.epub background.png video.mp4

# 配置管理
book2audio config --list
book2audio config --set voice zh-CN-XiaoyiNeural
```

### Python API

```python
from book2audio import TTSGenerator, AudioProcessor, VideoGenerator

# TTS 生成
tts = TTSGenerator()
await tts.generate_batch(segments, output_dir)

# 音频处理
processor = AudioProcessor()
processor.merge_audio_and_subtitles(input_dir, output_audio, output_subtitle)

# 视频生成
generator = VideoGenerator()
generator.generate_video(audio_file, subtitle_file, background, output_video)
```

## 配置参数

### TTS 参数

- `VOICE`: 语音选择（如 "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"）
- `RATE`: 语速调整（-50% 到 +50%）
- `VOLUME`: 音量调整（-50% 到 +50%）
- `PITCH`: 音调调整（-50Hz 到 +50Hz）
- `SEGMENT_SIZE`: 每段最大字数（推荐 500-1000）

### 视频参数

- `VIDEO_WIDTH`: 视频宽度（默认 1920）
- `VIDEO_HEIGHT`: 视频高度（默认 1080）
- `FONT_SIZE`: 字幕字体大小（默认 48）

## 支持的语音

### 中文语音
- zh-CN-XiaoxiaoNeural (晓晓，女声)
- zh-CN-YunxiNeural (云希，男声)
- zh-CN-YunjianNeural (云健，男声)
- zh-CN-XiaoyiNeural (晓伊，女声)
- zh-CN-YunyangNeural (云扬，男声)

### 其他语言
Edge TTS 支持多种语言，详见 Microsoft 文档。

## 注意事项

1. **网络要求**：Edge TTS 需要网络连接
2. **文件编码**：确保输入文本文件使用 UTF-8 编码
3. **路径分隔符**：Windows 下使用反斜杠 `\`，代码中会自动处理
4. **FFmpeg 路径**：根据你的安装位置修改 FFmpeg 路径
5. **内存使用**：大文件处理时注意内存占用

## 许可证

本项目仅供学习和个人使用，请遵守相关法律法规。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

- v2.0.0: 完全重构为模块化架构
  - 添加配置管理系统
  - 实现完整的日志系统
  - 创建命令行界面
  - 支持类型提示
  - 改进错误处理
  - 添加包管理和分发支持

- v1.2: 添加视频创建功能
- v1.1: 添加多格式电子书支持
- v1.0: 初始版本，支持基本 TTS 和字幕功能