# Book2Audio Makefile

.PHONY: help install test clean build

# 默认目标
help:
	@echo "Book2Audio - 电子书转音频工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install    安装依赖"
	@echo "  test       运行测试"
	@echo "  clean      清理临时文件"
	@echo "  build      构建包"
	@echo "  run        运行完整流程示例"
	@echo "  tts        运行TTS生成"
	@echo "  merge      合并音频和字幕"
	@echo "  video      生成视频"

# 安装依赖
install:
	pip install -r requirements.txt

# 开发安装
install-dev: install
	pip install -e .

# 运行测试
test:
	python tests/test_basic.py

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .eggs/
	rm -f book2audio.log

# 清理输出文件
clean-output:
	rm -rf output/
	rm -f *.mp3 *.srt *.mp4

# 构建包
build:
	python setup.py sdist bdist_wheel

# 运行完整流程示例
run:
	python -m book2audio all input.txt background.png output.mp4

# 运行TTS生成
tts:
	python -m book2audio tts input.txt

# 合并音频和字幕
merge:
	python -m book2audio merge output/ merged.mp3 merged.srt

# 生成视频
video:
	python -m book2audio video merged.mp3 merged.srt background.png output.mp4

# 显示配置
config:
	python -m book2audio config --list

# 安装到系统
install-system:
	pip install .

# 卸载
uninstall:
	pip uninstall book2audio</content>
<parameter name="filePath">d:\book2audio\Makefile