"""
Book2Audio - 优化版 TTS 生成器
使用模块化架构，支持配置管理和错误处理
"""
import asyncio
import time
import os
import re
import json
import tempfile
import subprocess
import shutil
from pathlib import Path

from config import config
from logger import logger
from utils import read_text_file, split_text_by_sentences, ensure_dir
from tts import TTSGenerator

# ========== 配置参数（统一从 config.ini 读取） ==========
INPUT_TXT = config.get('input_file')
OUTPUT_DIR = config.get('output_dir')
SEGMENT_SIZE = int(config.get('segment_size'))
VOICE = config.get('voice')
RATE = config.get('rate')
VOLUME = config.get('volume')
PITCH = config.get('pitch')
# =================================


async def main():
    """主函数"""
    print("=" * 60)
    print("Book2Audio - 优化版 TTS 生成器")
    print("=" * 60)
    print(f"语音: {VOICE}")
    print(f"语速: {RATE}")
    print(f"每段最大字数: {SEGMENT_SIZE}")
    print()

    # 1. 读取小说文件
    logger.info("📖 读取输入文件...")
    try:
        text = read_text_file(INPUT_TXT)
        logger.info(f"文件大小: {len(text)} 字符")
        logger.info(f"预览: {text[:100]}...")
    except Exception as e:
        logger.error(f"读取失败: {e}")
        return

    # 2. 分割文本
    logger.info("✂️ 分割文本...")
    segments = split_text_by_sentences(text, SEGMENT_SIZE)
    logger.info(f"共分为 {len(segments)} 段")

    # 3. 创建输出目录
    output_dir = ensure_dir(OUTPUT_DIR)

    # 4. 测试第一段
    logger.info("🔍 测试第一段...")
    tts_gen = TTSGenerator()

    test_audio = output_dir / "test_first.mp3"
    test_srt = output_dir / "test_first.srt"

    try:
        sub_count = await tts_gen.generate_segment(segments[0], test_audio, test_srt)
        if sub_count > 0:
            logger.info(f"✅ 测试成功！生成了 {sub_count} 条字幕")
            # 清理测试文件
            test_audio.unlink(missing_ok=True)
            test_srt.unlink(missing_ok=True)
        else:
            logger.warning("⚠️ 测试生成音频成功，但未生成字幕")
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return

    # 5. 批量生成
    logger.info("🎤 开始批量生成...")
    print("=" * 60)

    start_time = time.time()
    success_count = await tts_gen.generate_batch(segments, output_dir)

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    logger.info("✅ 完成！")
    logger.info(f"成功段数: {success_count}/{len(segments)}")
    logger.info(f"总耗时: {total_time:.1f} 秒")
    logger.info(f"输出目录: {output_dir}")
    print("\n💡 提示: 使用 'python -m book2audio merge' 合并音频和字幕")


if __name__ == "__main__":
    asyncio.run(main())


def read_txt_file(file_path):
    """读取 TXT 文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise Exception(f"无法读取文件: {file_path}")


def format_time(offset):
    """
    将 100ns 单位的时间戳转换为 SRT 格式 HH:MM:SS,mmm
    """
    seconds = offset / 10_000_000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    millis = int((secs - int(secs)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"


def parse_json_lines(content):
    """
    解析可能包含多行 JSON 的内容
    每行可能是一个完整的 JSON 对象
    """
    subs = []
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 尝试解析 JSON
        try:
            data = json.loads(line)
            if isinstance(data, dict) and data.get('type') == 'SentenceBoundary':
                start = data.get('offset')
                end = data.get('offset', 0) + data.get('duration', 0)
                text = data.get('text', '')
                if start is not None and text:
                    subs.append({
                        'start': start,
                        'end': end,
                        'text': text
                    })
        except json.JSONDecodeError:
            # 可能一行包含多个 JSON 对象
            # 尝试找到所有 {...} 块
            json_pattern = r'\{[^{}]*\}'
            matches = re.findall(json_pattern, line)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and data.get('type') == 'SentenceBoundary':
                        start = data.get('offset')
                        end = data.get('offset', 0) + data.get('duration', 0)
                        text = data.get('text', '')
                        if start is not None and text:
                            subs.append({
                                'start': start,
                                'end': end,
                                'text': text
                            })
                except:
                    continue

    return subs


async def generate_single_segment(text, audio_path, srt_path):
    """
    生成单个段落的音频和字幕
    使用命令行并捕获输出
    """
    try:
        # 使用临时文件存储字幕
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False, encoding='utf-8') as tmp:
            tmp_sub_path = tmp.name

        # 构建命令
        cmd = [
            "edge-tts",
            "--text", text,
            "--write-media", audio_path,
            "--write-subtitles", tmp_sub_path,
            "--voice", VOICE,
            "--rate", RATE
        ]

        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            # 检查是否有错误输出
            if result.stderr:
                print(f"\n    stderr: {result.stderr[:200]}")
            raise Exception(f"命令行执行失败")

        # 检查临时字幕文件
        if os.path.exists(tmp_sub_path) and os.path.getsize(tmp_sub_path) > 0:
            # 读取字幕文件内容
            with open(tmp_sub_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 JSON 内容
            subs = parse_json_lines(content)

            if subs:
                # 写入标准 SRT 文件
                with open(srt_path, 'w', encoding='utf-8-sig') as f:
                    for i, sub in enumerate(subs, 1):
                        f.write(f"{i}\n")
                        f.write(f"{format_time(sub['start'])} --> {format_time(sub['end'])}\n")
                        # 按标点换行
                        sub_text = sub['text']
                        sub_text = re.sub(r'([。！？])', r'\1\n', sub_text)
                        f.write(f"{sub_text}\n\n")

                # 清理临时文件
                try:
                    os.remove(tmp_sub_path)
                except:
                    pass

                return len(subs)
            else:
                # 没有找到有效字幕，尝试直接使用原文件（可能已经是 SRT）
                if os.path.exists(tmp_sub_path):
                    # 使用 shutil.move 支持跨磁盘
                    shutil.move(tmp_sub_path, srt_path)
                    return 1

        # 清理临时文件
        try:
            if os.path.exists(tmp_sub_path):
                os.remove(tmp_sub_path)
        except:
            pass

        return 0

    except subprocess.TimeoutExpired:
        raise Exception("生成超时（超过120秒）")
    except Exception as e:
        raise e


async def generate_with_progress(segments, output_dir):
    """批量生成，带进度显示"""
    success_count = 0
    total = len(segments)

    for i, seg in enumerate(segments):
        audio_path = os.path.join(output_dir, f"part_{i + 1:04d}.mp3")
        srt_path = os.path.join(output_dir, f"part_{i + 1:04d}.srt")

        # 显示文本预览
        preview = seg[:50] + "..." if len(seg) > 50 else seg
        print(f"[{i + 1}/{total}] 生成中... ({len(seg)}字)", end=" ")
        start_time = time.time()

        try:
            sub_count = await generate_single_segment(seg, audio_path, srt_path)
            elapsed = time.time() - start_time

            if sub_count > 0:
                print(f"✅ 完成 ({elapsed:.1f}秒) - 字幕 {sub_count} 句")
            elif os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"✅ 完成 ({elapsed:.1f}秒) - 音频已生成")
            else:
                print(f"❌ 失败 - 未生成任何文件")
                continue

            success_count += 1

        except Exception as e:
            print(f"❌ 失败: {e}")

        # 短暂延迟
        await asyncio.sleep(0.5)

    return success_count


async def main():
    print("=" * 60)
    print("Edge TTS 小说转语音（跨磁盘修复版）")
    print("=" * 60)
    print(f"音色: {VOICE}")
    print(f"语速: {RATE}")
    print(f"每段最大字数: {SEGMENT_SIZE}")
    print()

    # 1. 读取小说
    print("📖 读取小说文件...")
    try:
        full_text = read_txt_file(INPUT_TXT)
        print(f"   文件大小: {len(full_text)} 字符")
        print(f"   预览: {full_text[:100]}...")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return

    # 2. 分割文本
    print("✂️  分割文本...")
    segments = split_text_by_sentences(full_text, SEGMENT_SIZE)
    print(f"   共分为 {len(segments)} 段")

    # 3. 先测试第一段
    print("\n🔍 测试第一段...")
    test_audio = os.path.join(OUTPUT_DIR, "test_first.mp3")
    test_srt = os.path.join(OUTPUT_DIR, "test_first.srt")

    try:
        sub_count = await generate_single_segment(segments[0], test_audio, test_srt)
        if sub_count > 0:
            print(f"   ✅ 测试成功！生成了 {sub_count} 条字幕")
            # 清理测试文件
            if os.path.exists(test_audio):
                os.remove(test_audio)
            if os.path.exists(test_srt):
                os.remove(test_srt)
        else:
            print(f"   ⚠️ 测试生成音频成功，但未生成字幕")
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return

    # 4. 批量生成
    print("\n🎤 开始批量生成语音和字幕...")
    print("=" * 60)

    start_time = time.time()
    success_count = await generate_with_progress(segments, OUTPUT_DIR)

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✅ 完成！")
    print(f"   成功段数: {success_count}/{len(segments)}")
    print(f"   总耗时: {total_time:.1f} 秒")
    print(f"   输出目录: {OUTPUT_DIR}")
    print("\n💡 提示: 用 PotPlayer 打开 MP3 文件，字幕会自动加载")


if __name__ == "__main__":
    asyncio.run(main())