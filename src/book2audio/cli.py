"""Book2Audio 命令行接口"""
import argparse
import asyncio
import sys
from pathlib import Path

from .config import config
from .logger import logger
from .utils import read_text_file, split_text_by_sentences, ensure_dir
from .tts import TTSGenerator
from .audio_processor import AudioProcessor
from .video_generator import VideoGenerator
from .extract_text import extract_text


class Book2AudioCLI:
    """Book2Audio 命令行接口"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Book2Audio - 将电子书转换为音频和视频",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  book2audio tts input.txt                    # 生成 TTS 音频和字幕
  book2audio merge output/ book.mp3 book.srt  # 合并音频和字幕
  book2audio video book.mp3 book.srt bg.jpg output.mp4  # 生成视频
  book2audio all input.txt bg.jpg output.mp4  # 完整流程
            """
        )
        self.subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        self._setup_parsers()

    def _setup_parsers(self):
        """设置子命令解析器"""
        tts_parser = self.subparsers.add_parser('tts', help='生成 TTS 音频和字幕')
        tts_parser.add_argument('input_file', help='输入文本文件')
        tts_parser.add_argument('-o', '--output-dir', default=config.output_dir, help='输出目录')
        tts_parser.add_argument('-v', '--voice', default=config.voice, help='语音选择')
        tts_parser.add_argument('-r', '--rate', default=config.rate, help='语速')
        tts_parser.add_argument('-s', '--segment-size', type=int, default=config.segment_size, help='分段大小')

        merge_parser = self.subparsers.add_parser('merge', help='合并音频和字幕')
        merge_parser.add_argument('input_dir', help='输入目录')
        merge_parser.add_argument('output_audio', help='输出音频文件')
        merge_parser.add_argument('output_subtitle', help='输出字幕文件')

        video_parser = self.subparsers.add_parser('video', help='生成视频')
        video_parser.add_argument('audio_file', help='音频文件')
        video_parser.add_argument('subtitle_file', help='字幕文件')
        video_parser.add_argument('background_image', help='背景图片')
        video_parser.add_argument('output_video', help='输出视频文件')

        all_parser = self.subparsers.add_parser('all', help='完整转换流程')
        all_parser.add_argument('input_file', help='输入文件')
        all_parser.add_argument('background_image', help='背景图片')
        all_parser.add_argument('output_video', help='输出视频文件')
        all_parser.add_argument('-o', '--output-dir', default=config.output_dir, help='临时输出目录')

        config_parser = self.subparsers.add_parser('config', help='显示/修改配置')
        config_parser.add_argument('--list', action='store_true', help='显示所有配置')
        config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置项')

    async def run_tts(self, args):
        """运行 TTS 命令"""
        logger.info("=" * 60)
        logger.info("Book2Audio - TTS 生成")
        logger.info("=" * 60)

        try:
            if Path(args.input_file).suffix.lower() in ['.epub', '.mobi', '.azw3', '.pdf']:
                logger.info("检测到电子书格式，正在提取文本...")
                text = extract_text(args.input_file)
            else:
                text = read_text_file(args.input_file)
            logger.info(f"文本长度：{len(text)} 字符")
        except Exception as e:
            logger.error(f"读取输入文件失败：{e}")
            return

        segments = split_text_by_sentences(text, args.segment_size)
        logger.info(f"分割为 {len(segments)} 段")

        output_dir = ensure_dir(args.output_dir)
        tts_gen = TTSGenerator()
        tts_gen.voice = args.voice
        tts_gen.rate = args.rate

        success_count = await tts_gen.generate_batch(segments, output_dir)
        logger.info(f"TTS 生成完成：{success_count}/{len(segments)} 成功")

    def run_merge(self, args):
        """运行合并命令"""
        logger.info("Book2Audio - 合并音频和字幕")
        processor = AudioProcessor()
        success = processor.merge_audio_and_subtitles(
            args.input_dir, args.output_audio, args.output_subtitle
        )
        if success:
            logger.info("合并完成")
        else:
            logger.error("合并失败")

    def run_video(self, args):
        """运行视频命令"""
        logger.info("Book2Audio - 生成视频")
        try:
            generator = VideoGenerator()
            success = generator.generate_video(
                args.audio_file, args.subtitle_file,
                args.background_image, args.output_video
            )
            if success:
                logger.info("视频生成完成")
            else:
                logger.error("视频生成失败")
        except Exception as e:
            logger.error(f"视频生成异常：{e}")

    async def run_all(self, args):
        """运行完整流程"""
        logger.info("Book2Audio - 完整转换流程")
        logger.info("=" * 60)

        await self.run_tts(args)

        output_audio = Path(args.output_dir) / "merged.mp3"
        output_subtitle = Path(args.output_dir) / "merged.srt"

        merge_args = argparse.Namespace(
            input_dir=args.output_dir,
            output_audio=str(output_audio),
            output_subtitle=str(output_subtitle)
        )
        self.run_merge(merge_args)

        video_args = argparse.Namespace(
            audio_file=str(output_audio),
            subtitle_file=str(output_subtitle),
            background_image=args.background_image,
            output_video=args.output_video
        )
        self.run_video(video_args)

    def run_config(self, args):
        """运行配置命令"""
        if args.list:
            print("当前配置:")
            for key in config.defaults.keys():
                value = config.get(key)
                print(f"  {key}: {value}")
        elif args.set:
            key, value = args.set
            config.set(key, value)
            print(f"已设置 {key} = {value}")
        else:
            self.parser.parse_args(['config', '--help'])

    async def run(self):
        """运行 CLI"""
        args = self.parser.parse_args()

        if not args.command:
            self.parser.print_help()
            return

        try:
            if args.command == 'tts':
                await self.run_tts(args)
            elif args.command == 'merge':
                self.run_merge(args)
            elif args.command == 'video':
                self.run_video(args)
            elif args.command == 'all':
                await self.run_all(args)
            elif args.command == 'config':
                self.run_config(args)
        except KeyboardInterrupt:
            logger.info("用户中断")
        except Exception as e:
            logger.error(f"执行失败：{e}")
            sys.exit(1)


def main():
    """主入口函数"""
    cli = Book2AudioCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
