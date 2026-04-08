"""
多格式电子书文本提取器
支持 EPUB, MOBI, AZW3, PDF, TXT 等格式
"""
import os
import re

# ========== 根据安装的库选择性导入 ==========
try:
    import ebooklib
    from ebooklib import epub

    EBOKLIB_AVAILABLE = True
except ImportError:
    EBOKLIB_AVAILABLE = False
    print("⚠️ ebooklib 未安装，EPUB格式不可用。运行: pip install EbookLib")

try:
    import mobi

    MOBI_AVAILABLE = True
except ImportError:
    MOBI_AVAILABLE = False
    print("⚠️ mobi 未安装，MOBI/AZW3格式不可用。运行: pip install mobi")

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ PyMuPDF 未安装，PDF格式不可用。运行: pip install PyMuPDF")

try:
    from pressor import pressor

    PRESSOR_AVAILABLE = True
except ImportError:
    PRESSOR_AVAILABLE = False
    print("⚠️ pressor 未安装，将使用备用方案。运行: pip install pressor")


def extract_from_epub(file_path):
    """从 EPUB 文件提取文本"""
    if not EBOKLIB_AVAILABLE:
        return None

    try:
        book = epub.read_epub(file_path)
        text_parts = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8', errors='ignore')
                # 简单去除 HTML 标签
                text = re.sub(r'<[^>]+>', ' ', content)
                text = re.sub(r'\s+', ' ', text)
                text_parts.append(text.strip())

        return '\n\n'.join(text_parts)
    except Exception as e:
        print(f"EPUB 解析失败: {e}")
        return None


def extract_from_mobi(file_path):
    """从 MOBI/AZW3 文件提取文本"""
    if not MOBI_AVAILABLE:
        return None

    try:
        # mobi 库返回 (tempdir, filepath)
        result = mobi.extract(file_path)
        if result and len(result) >= 2:
            extracted_file = result[1]
            with open(extracted_file, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return text
        return None
    except Exception as e:
        print(f"MOBI/AZW3 解析失败: {e}")
        return None


def extract_from_pdf(file_path):
    """从 PDF 文件提取文本"""
    if not PYMUPDF_AVAILABLE:
        return None

    try:
        doc = fitz.open(file_path)
        text_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_parts.append(page.get_text())
        return '\n\n'.join(text_parts)
    except Exception as e:
        print(f"PDF 解析失败: {e}")
        return None


def extract_from_txt(file_path):
    """从 TXT 文件提取文本"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise Exception(f"无法读取文件: {file_path}")


def extract_text(file_path):
    """
    通用文本提取函数，自动根据文件扩展名选择解析方式
    支持格式: .txt, .epub, .mobi, .azw3, .pdf
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        return extract_from_txt(file_path)
    elif ext == '.epub':
        return extract_from_epub(file_path)
    elif ext in ['.mobi', '.azw3', '.azw']:
        return extract_from_mobi(file_path)
    elif ext == '.pdf':
        return extract_from_pdf(file_path)
    else:
        # 尝试使用 pressor 作为备用（支持更多格式）
        if PRESSOR_AVAILABLE:
            try:
                return pressor(file_path)
            except:
                pass
        raise ValueError(f"不支持的文件格式: {ext}")


def extract_and_save(input_path, output_txt_path):
    """提取文本并保存为 TXT 文件"""
    print(f"📖 正在提取: {input_path}")
    text = extract_text(input_path)

    if text is None:
        print(f"❌ 提取失败")
        return False

    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ 已保存为: {output_txt_path}")
    print(f"   文本长度: {len(text)} 字符")
    return True


if __name__ == "__main__":
    # 测试示例
    import sys

    if len(sys.argv) < 2:
        print("用法: python extract_text.py <电子书文件路径>")
        print("支持格式: .txt, .epub, .mobi, .azw3, .pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] + "_extracted.txt"

    extract_and_save(input_file, output_file)