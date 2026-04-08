import os
import re
import subprocess
import shutil


# ========== 配置参数 ==========
AUDIO_FILE = r"D:\book2audio\novel.mp3"  # 音频文件
SUBTITLE_FILE = r"D:\book2audio\novel.srt"  # 字幕文件
BACKGROUND_IMAGE = r"D:\book2audio\background.jpg"  # 背景图片
OUTPUT_VIDEO = r"D:\book2audio\output_video.mp4"  # 输出视频

FFMPEG_PATH = r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffprobe.exe"

os.environ["PATH"] += os.pathsep + r"C:\Users\hou_m\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
print(f"使用 ffmpeg: {FFMPEG_PATH}")
print(f"使用 ffprobe: {FFPROBE_PATH}")




# 视频参数
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FONT_SIZE = 48


# =================================
def create_video_working():
    """使用绝对路径和正确转义的工作版本"""

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("❌ 未找到 ffmpeg")
        return False

    # 检查文件
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ 音频不存在: {AUDIO_FILE}")
        return False

    if not os.path.exists(SUBTITLE_FILE):
        print(f"❌ 字幕不存在: {SUBTITLE_FILE}")
        return False

    # 使用正斜杠并转义路径
    audio_path = AUDIO_FILE.replace('\\', '/')
    subtitle_path = SUBTITLE_FILE.replace('\\', '/')
    output_path = OUTPUT_VIDEO.replace('\\', '/')

    print(f"音频: {audio_path}")
    print(f"字幕: {subtitle_path}")
    print()

    # 准备背景图片
    if os.path.exists(BACKGROUND_IMAGE):
        print("准备背景图片...")
        # 创建调整后的背景图片
        temp_bg = "temp_bg.jpg"
        resize_cmd = [
            ffmpeg, "-y",
            "-i", BACKGROUND_IMAGE,
            "-vf",
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=1,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
            "-frames:v", "1",
            temp_bg
        ]
        subprocess.run(resize_cmd, capture_output=True)
        bg_file = temp_bg
    else:
        print("使用黑色背景")
        bg_file = None

    # 使用最简单的命令结构
    if bg_file:
        cmd = f'"{ffmpeg}" -y -loop 1 -i "{bg_file}" -i "{audio_path}" -filter_complex "[0:v]subtitles={subtitle_path}:force_style=\'FontSize={FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=1\'[v]" -map "[v]" -map 1:a -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest "{output_path}"'
    else:
        cmd = f'"{ffmpeg}" -y -f lavfi -i color=c=black:s={VIDEO_WIDTH}x{VIDEO_HEIGHT} -i "{audio_path}" -filter_complex "[0:v]subtitles={subtitle_path}:force_style=\'FontSize={FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=1\'[v]" -map "[v]" -map 1:a -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest "{output_path}"'

    print("\n🎬 正在生成视频...")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=False)

        # 清理临时文件
        if bg_file and os.path.exists(bg_file):
            os.remove(bg_file)

        if result.returncode == 0 and os.path.exists(OUTPUT_VIDEO):
            size = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
            print(f"\n✅ 视频生成成功！")
            print(f"   文件: {OUTPUT_VIDEO}")
            print(f"   大小: {size:.1f} MB")
            return True
        else:
            print(f"\n❌ 视频生成失败")
            if result.stderr:
                try:
                    err = result.stderr.decode('utf-8', errors='ignore')
                    # 显示详细错误
                    for line in err.split('\n'):
                        if 'Error' in line or 'error' in line:
                            print(f"   {line}")
                except:
                    pass
            return False

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False


def main():
    print("=" * 60)
    print("朗读视频生成器")
    print("=" * 60)

    success = create_video_working()

    if success:
        print("\n" + "=" * 60)
        print("✅ 完成！")
    else:
        print("\n" + "=" * 60)
        print("💡 推荐方案:")
        print("   直接用 PotPlayer 播放音频+字幕")
        print(f"   1. 打开 PotPlayer")
        print(f"   2. 将 {AUDIO_FILE} 拖入窗口")
        print(f"   3. 按 Alt+H 调整字幕位置")
        print(f"   4. 按 Ctrl+[ / ] 调整字幕大小")


if __name__ == "__main__":
    main()