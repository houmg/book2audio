import asyncio
import edge_tts
import os
import re
import time
from config import config

# ========== 配置参数 (从 config.ini 读取) ==========
INPUT_TXT = config.get('input_file')  # 输入的小说文件
OUTPUT_DIR = config.get('output_dir')  # 输出目录
SEGMENT_SIZE = int(config.get('segment_size'))  # 每段最大字数
VOICE = config.get('voice')  # 音色选择
RATE = config.get('rate')  # 语速调整
VOLUME = config.get('volume')  # 音量调整
PITCH = config.get('pitch')  # 音调调整
# =================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


def split_text(text, max_len=SEGMENT_SIZE):
    """将文本按句子分割成小段，每段不超过 max_len 字"""
    # 按中文标点分割
    sentences = re.split(r'(?<=[。！？；])|(?<=\.{3})|(?<=\n)', text)

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
                # 超长句子强制切分
                for i in range(0, len(sent), max_len):
                    segments.append(sent[i:i + max_len])
                current = ""
            else:
                current = sent
    if current:
        segments.append(current)
    return segments


def read_txt_file(file_path):
    """读取 TXT 文件，自动处理编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise Exception(f"无法读取文件: {file_path}")


async def text_to_speech(text, output_path):
    """将文本转换为语音并保存"""
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE,
        volume=VOLUME,
        pitch=PITCH
    )
    await communicate.save(output_path)


async def batch_generate(segments, output_dir):
    """批量生成音频"""
    tasks = []
    for i, seg in enumerate(segments):
        # 生成音频的文件路径
        audio_file = os.path.join(output_dir, f"part_{i + 1:04d}.mp3")
        # 调用生成音频的函数
        tasks.append(text_to_speech(seg, audio_file))

    # 并发执行（控制并发数避免网络拥堵）
    semaphore = asyncio.Semaphore(5)  # 同时最多 5 个任务

    async def bounded_task(task, idx, seg):
        async with semaphore:
            start = time.time()
            print(f"[{idx + 1}/{len(segments)}] 生成中...", end=" ")
            await task
            elapsed = time.time() - start
            # 更新提示信息
            print(f"✅ 完成 ({elapsed:.1f}秒，{len(seg)}字)")

    tasks_with_info = [
        bounded_task(task, i, seg)
        for i, (task, seg) in enumerate(zip(tasks, segments))
    ]

    await asyncio.gather(*tasks_with_info)



async def main():
    print("=" * 50)
    print("Edge TTS 小说转语音")
    print("=" * 50)
    print(f"音色: {VOICE}")
    print(f"语速: {RATE}, 音量: {VOLUME}, 音调: {PITCH}\n")

    # 1. 读取小说
    print("📖 读取小说文件...")
    try:
        full_text = read_txt_file(INPUT_TXT)
        print(f"   文件大小: {len(full_text)} 字符")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return

    # 2. 分割文本
    print("✂️  分割文本...")
    segments = split_text(full_text)
    print(f"   共分为 {len(segments)} 段")

    # 3. 生成音频
    print("\n🎤 开始生成语音...")
    print("=" * 50)

    start_time = time.time()
    await batch_generate(segments, OUTPUT_DIR)

    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"✅ 全部完成！")
    print(f"   总段数: {len(segments)}")
    print(f"   总耗时: {total_time:.1f} 秒")
    print(f"   平均每段: {total_time / len(segments):.1f} 秒")
    print(f"   输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())