"""
Book2Audio setup.py
"""
from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="book2audio",
    version="2.0.0",
    author="Book2Audio Team",
    author_email="",
    description="将电子书转换为音频和视频的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/book2audio",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "book2audio=book2audio.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
