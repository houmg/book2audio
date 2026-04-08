#!/usr/bin/env python3
"""
Book2Audio 演示脚本
展示如何使用优化后的模块化架构
"""

import asyncio
from pathlib import Path

from config import config
from utils import read_text_file, split_text_by_sentences
from tts import TTSGenerator


async def demo():
    """演示函数"""
    print("🎵 Book2Audio v2.0 演示")
    print("=" * 50)

    # 1. 检查输入文件
    input_file = Path(config.input_file)
    if not input_file.exists():
        print(f"❌ 输入文件不存在: {input_file}")
        print("请创建 input.txt 文件或修改 config.ini 中的 input_file 设置")
        return

    # 2. 读取和分割文本
    print("📖 读取文本文件...")
    try:
        text = read_text_file(str(input_file))
        print(f"文本长度: {len(text)} 字符")

        segments = split_text_by_sentences(text, config.segment_size)
        print(f"分割为 {len(segments)} 段")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    # 3. 创建输出目录
    output_dir = Path(config.output_dir)
    output_dir.mkdir(exist_ok=True)

    # 4. 初始化TTS生成器
    print("🎤 初始化TTS生成器...")
    tts = TTSGenerator()
    print(f"语音: {tts.voice}")
    print(f"语速: {tts.rate}")

    # 5. 生成演示（仅前3段）
    demo_segments = segments[:3]  # 只演示前3段
    print(f"\n🚀 开始生成演示音频（{len(demo_segments)}段）...")

    success_count = await tts.generate_batch(demo_segments, output_dir)

    print("\n" + "=" * 50)
    print("✅ 演示完成！")
    print(f"成功生成: {success_count}/{len(demo_segments)} 段")
    print(f"输出目录: {output_dir.absolute()}")
    print("\n💡 完整使用:")
    print("  python -m book2audio tts input.txt    # 生成所有段落")
    print("  python -m book2audio merge output/ merged.mp3 merged.srt  # 合并文件")
    print("  python -m book2audio all input.txt background.jpg video.mp4  # 完整流程")


if __name__ == "__main__":
    asyncio.run(demo())