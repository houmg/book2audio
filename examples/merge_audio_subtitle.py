import os
import re
import glob
from pydub import AudioSegment

# ========== 手动指定 ffmpeg 路径（重要！）==========
# 根据你的 ffmpeg 位置，选择一个正确的路径
# 选项1：如果你是从 gyan.dev 下载的
AudioSegment.converter = r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffprobe.exe"

# 选项2：如果 ffmpeg 在系统 PATH 中但 Python 找不到
# 可以用这个临时添加到环境变量
os.environ["PATH"] += os.pathsep + r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
# =================================================

# ========== 配置参数 ==========
INPUT_DIR = r"D:\book2audio\output"
OUTPUT_AUDIO = r"D:\book2audio\春.mp3"
OUTPUT_SUBTITLE = r"D:\book2audio\春.srt"


# =================================


def get_file_list(input_dir):
    """获取排序后的音频和字幕文件列表"""
    audio_files = sorted(glob.glob(os.path.join(input_dir, "part_*.mp3")))
    subtitle_files = [f.replace('.mp3', '.srt') for f in audio_files]
    return audio_files, subtitle_files


def format_time(seconds):
    """将秒转换为 SRT 时间格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse_srt_time(time_str):
    """将 SRT 时间格式 HH:MM:SS,mmm 转换为秒"""
    hours, minutes, rest = time_str.split(':')
    seconds, millis = rest.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def merge_audio_files(audio_files, output_path):
    """合并多个 MP3 文件"""
    print("🎵 合并音频文件...")

    if not audio_files:
        print("❌ 没有找到音频文件")
        return 0

    combined = AudioSegment.empty()
    total_duration = 0

    for i, audio_file in enumerate(audio_files):
        print(f"   合并 [{i + 1}/{len(audio_files)}]: {os.path.basename(audio_file)}")
        audio = AudioSegment.from_mp3(audio_file)
        combined += audio
        total_duration += len(audio)

    combined.export(output_path, format="mp3")
    print(f"✅ 音频合并完成: {output_path}")
    print(f"   总时长: {total_duration / 1000:.1f} 秒 ({total_duration / 1000 / 60:.1f} 分钟)\n")

    return total_duration / 1000


def merge_subtitle_files(subtitle_files, audio_durations, output_path):
    """合并多个 SRT 文件，重新计算时间轴"""
    print("📝 合并字幕文件...")

    if not subtitle_files:
        print("❌ 没有找到字幕文件")
        return

    all_subs = []
    cumulative_time = 0
    subtitle_counter = 1

    for i, srt_file in enumerate(subtitle_files):
        if not os.path.exists(srt_file):
            print(f"   ⚠️ 字幕文件不存在: {os.path.basename(srt_file)}，跳过")
            continue

        print(f"   处理 [{i + 1}/{len(subtitle_files)}]: {os.path.basename(srt_file)}")

        with open(srt_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        blocks = re.split(r'\n\s*\n', content.strip())

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue

            time_line = lines[1] if len(lines) > 1 else ""
            text_lines = lines[2:] if len(lines) > 2 else []

            if '-->' in time_line:
                start_str, end_str = time_line.split(' --> ')
                start_ms = parse_srt_time(start_str)
                end_ms = parse_srt_time(end_str)

                new_start = cumulative_time + start_ms
                new_end = cumulative_time + end_ms

                all_subs.append({
                    'index': subtitle_counter,
                    'start': new_start,
                    'end': new_end,
                    'text': '\n'.join(text_lines).strip()
                })
                subtitle_counter += 1

        if i < len(audio_durations):
            cumulative_time += audio_durations[i]

    with open(output_path, 'w', encoding='utf-8-sig') as f:
        for sub in all_subs:
            f.write(f"{sub['index']}\n")
            f.write(f"{format_time(sub['start'])} --> {format_time(sub['end'])}\n")
            f.write(f"{sub['text']}\n\n")

    print(f"✅ 字幕合并完成: {output_path}")
    print(f"   总字幕数: {len(all_subs)}")


def get_audio_durations(audio_files):
    """获取每个音频文件的时长（秒）"""
    durations = []
    for audio_file in audio_files:
        audio = AudioSegment.from_mp3(audio_file)
        durations.append(len(audio) / 1000)
    return durations


def main():
    print("=" * 60)
    print("音频和字幕合并工具")
    print("=" * 60)
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出音频: {OUTPUT_AUDIO}")
    print(f"输出字幕: {OUTPUT_SUBTITLE}")
    print()

    audio_files, subtitle_files = get_file_list(INPUT_DIR)

    if not audio_files:
        print("❌ 没有找到音频文件（part_*.mp3）")
        return

    print(f"找到 {len(audio_files)} 个音频文件\n")

    print("📊 读取音频时长...")
    audio_durations = get_audio_durations(audio_files)
    for i, (file, dur) in enumerate(zip(audio_files, audio_durations)):
        print(f"   {os.path.basename(file)}: {dur:.1f} 秒")
    print()

    total_duration = merge_audio_files(audio_files, OUTPUT_AUDIO)
    merge_subtitle_files(subtitle_files, audio_durations, OUTPUT_SUBTITLE)

    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print(f"音频文件: {OUTPUT_AUDIO}")
    print(f"字幕文件: {OUTPUT_SUBTITLE}")
    print("\n💡 使用提示:")
    print("   1. 用 PotPlayer 打开 MP3 文件，字幕会自动加载")
    print("   2. 如果字幕没有自动加载，将 SRT 文件拖入播放器窗口")


if __name__ == "__main__":
    main()