"""
Book2Audio 测试文件
"""
import asyncio
import tempfile
import os
from pathlib import Path

from config import config
from utils import split_text_by_sentences
from tts import TTSGenerator


async def test_tts_basic():
    """测试基本TTS功能"""
    print("测试 TTS 基本功能...")

    # 测试文本分割
    test_text = "这是一个测试句子。这是第二个句子！这是第三个句子？"
    segments = split_text_by_sentences(test_text, 20)
    assert len(segments) == 3, f"期望3段，实际{len(segments)}段"

    # 测试TTS生成器
    tts = TTSGenerator()

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "test.mp3"
        srt_path = Path(temp_dir) / "test.srt"

        # 生成单个段落
        sub_count = await tts.generate_segment("你好，世界！", audio_path, srt_path)

        # 检查文件是否生成
        assert audio_path.exists(), "音频文件未生成"
        assert audio_path.stat().st_size > 0, "音频文件为空"

        print("✅ 基本TTS测试通过")


def test_config():
    """测试配置系统"""
    print("测试配置系统...")

    # 测试默认配置
    assert config.voice == "zh-CN-XiaoxiaoNeural"
    assert config.segment_size == 500

    print("✅ 配置测试通过")


def test_utils():
    """测试工具函数"""
    print("测试工具函数...")

    from utils import format_time_srt, parse_srt_time

    # 测试时间格式转换
    time_str = format_time_srt(65.5)  # 1分5.5秒
    assert time_str == "00:01:05,500"

    seconds = parse_srt_time("00:01:05,500")
    assert abs(seconds - 65.5) < 0.001

    print("✅ 工具函数测试通过")


async def run_tests():
    """运行所有测试"""
    print("开始 Book2Audio 测试...")
    print("=" * 50)

    try:
        test_config()
        test_utils()
        await test_tts_basic()

        print("=" * 50)
        print("🎉 所有测试通过！")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_tests())</content>
<parameter name="filePath">d:\book2audio\test_basic.py