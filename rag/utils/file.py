from typing import Dict, List, Optional, Tuple, Union

import os
import re
import PyPDF2
import markdown
import html2text
from docx import Document
import json
from tqdm import tqdm
import tiktoken
from bs4 import BeautifulSoup

""" CONFIG """
tiktoken_cache_dir = "./"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
# TODO what‘s this used for？
enc = tiktoken.get_encoding("cl100k_base")


class ReadFiles:
    """
    class to read files
    """
    _file_type = ['.md', '.txt', '.pdf', '.docx', '.doc']
    def __init__(self, path: str, dir=False) -> None:
        self._path = path
        self.file_list = self.get_files() if dir else [path]

    def get_files(self):
        # args：dir_path，目标文件夹路径
        file_list = []
        for filepath, dirnames, filenames in os.walk(self._path):
            # os.walk 函数将递归遍历指定文件夹
            for filename in filenames:
                # 通过后缀名判断文件类型是否满足要求
                if any(filename.endswith(ext) for ext in self._file_types):
                    file_list.append(os.path.join(filepath, filename))
        return file_list

    def get_content(self, max_token_len: int = 1600, min_token_len : int=600, cover_content: int = 150):
        """
        循环目录下文件用。
        :param max_token_len:
        :param min_token_len:
        :param cover_content:
        :return:
        """
        docs = []
        # 读取文件内容
        for file in self.file_list:
            content = self.read_file_content(file)
            # chunk只涉及min
            # chunk_content = self.get_chunk(
            #     content, min_token_len=min_token_len, cover_content=cover_content)
            chunk_content = self.get_chunk2(
                content, min_token_len=min_token_len, max_token_len=max_token_len, cover_content=cover_content)
            docs.extend(chunk_content)
        return docs

    @classmethod
    def get_chunk(cls, text: str, min_token_len: int = 600, cover_content: int = 150):
        chunk_text = []

        curr_len = 0
        curr_chunk = ''

        lines = text.split('\n')  # 假设以换行符分割文本为行

        for line in lines:
            line = line.replace(' ', '')
            line_len = len(enc.encode(line))
            if line_len > min_token_len:
                print('warning line_len = ', line_len)
            if curr_len + line_len <= min_token_len:
                curr_chunk += line
                curr_chunk += '\n'
                curr_len += line_len
                curr_len += 1
            else:
                if curr_chunk:
                    chunk_text.append(curr_chunk)
                    curr_chunk = curr_chunk[-cover_content:] + line
                    curr_len = line_len + cover_content

        if curr_chunk:
            chunk_text.append(curr_chunk)

        return chunk_text

    @classmethod
    def get_chunk2(cls, text: str, min_token_len: int = 600, max_token_len: int = 1600, cover_content: int = 150):
        chunk_text = []
        chunk_lenth = []

        curr_len = 0
        curr_chunk = ''

        lines = text.split('\n')  # 假设以换行符分割文本为行
        for line in lines:
            line = line.replace(' ', '')
            line_len = len(enc.encode(line))
            if curr_len > max_token_len:
                while (curr_len > max_token_len):
                    split_a = enc.encode(curr_chunk)[:max_token_len]
                    split_b = enc.encode(curr_chunk)[max_token_len:]
                    curr_chunk = enc.decode(split_a)
                    chunk_text.append(curr_chunk)
                    chunk_lenth.append(max_token_len)
                    curr_chunk = curr_chunk[-cover_content:] + enc.decode(split_b)
                    curr_len = cover_content + curr_len - max_token_len
            else:
                if (curr_len <= min_token_len):
                    curr_chunk += line
                    curr_chunk += '\n'
                    curr_len += line_len
                    curr_len += 1
                else:
                    chunk_text.append(curr_chunk)
                    chunk_lenth.append(curr_len)
                    curr_chunk = curr_chunk[-cover_content:] + line
                    curr_len = line_len + cover_content
        if curr_chunk:
            chunk_text.append(curr_chunk)
            chunk_lenth.append(curr_len)
        return chunk_text

    def get_chunk_by_title(self, title):
        """
        通过对应 title 的方式来分块，具有一定的局限性；目前是为 docx 的扩展。
        :param title:
        :return:
        """
        chunk_text = []

        contents = self.read_docx(self.file_list[0])
        chunk = ""
        for idx, text in enumerate(contents):
            if text in title:
                if chunk:
                    chunk_text.append(chunk)
                chunk = text + "："
            else:
                chunk += text
        if chunk:
            chunk_text.append(chunk)
        return chunk_text

    @classmethod
    def read_file_content(cls, file_path: str):
        # 根据文件扩展名选择读取方法
        if file_path.endswith('.pdf'):
            return cls.read_pdf(file_path)
        elif file_path.endswith('.md'):
            return cls.read_markdown(file_path)
        elif file_path.endswith('.txt'):
            return cls.read_text(file_path)
        elif file_path.endswith('.docx'):
            return cls.read_docx(file_path)
        else:
            raise ValueError("Unsupported file type")

    @classmethod
    def read_pdf(cls, file_path: str):
        # 读取PDF文件
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text

    @classmethod
    def read_markdown(cls, file_path: str):
        # 读取Markdown文件
        with open(file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
            html_text = markdown.markdown(md_text)
            # 使用BeautifulSoup从HTML中提取纯文本
            soup = BeautifulSoup(html_text, 'html.parser')
            plain_text = soup.get_text()
            # 使用正则表达式移除网址链接
            text = re.sub(r'http\S+', '', plain_text) 
            return text

    @classmethod
    def read_text(cls, file_path: str):
        # 读取文本文件
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @classmethod
    def read_docx(cls, file_path: str):
        # 加载文档
        doc = Document(file_path)
        # 读取每个段落并存储在列表中
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip() != '']
        return paragraphs


class Documents:
    """
        获取已分好类的json格式文档
    """
    def __init__(self, path: str = '') -> None:
        self.path = path
    
    def get_content(self):
        with open(self.path, mode='r', encoding='utf-8') as f:
            content = json.load(f)
        return content
