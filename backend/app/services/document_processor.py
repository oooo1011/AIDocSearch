import os
from typing import List, Optional
import PyPDF2
import docx2txt
from .vector_store import VectorStore

class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStore()
        self.chunk_size = 1000
        self.chunk_overlap = 200

    def process_document(self, file_path: str, document_id: str) -> str:
        """处理文档并存储到向量数据库"""
        # 读取文档内容
        content = self._read_document(file_path)
        if not content:
            return "文档内容为空"

        # 分块
        chunks = self._split_text(content)
        
        # 存储到向量数据库
        self.vector_store.add_texts(chunks, document_id)
        
        return f"成功处理文档，共{len(chunks)}个文本块"

    def _read_document(self, file_path: str) -> Optional[str]:
        """读取不同格式的文档"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                return self._read_pdf(file_path)
            elif file_extension == '.docx':
                return self._read_docx(file_path)
            elif file_extension == '.txt':
                return self._read_txt(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")
        except Exception as e:
            print(f"读取文档失败: {str(e)}")
            return None

    def _read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _read_docx(self, file_path: str) -> str:
        """读取DOCX文件"""
        return docx2txt.process(file_path)

    def _read_txt(self, file_path: str) -> str:
        """读取TXT文件"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _split_text(self, text: str) -> List[str]:
        """将文本分割成块"""
        chunks = []
        start = 0
        
        while start < len(text):
            # 找到块的结束位置
            end = start + self.chunk_size
            
            # 如果不是文本的末尾，尝试在句子边界分割
            if end < len(text):
                # 在最后一个句号、问号或感叹号处分割
                last_period = max(
                    text.rfind('.', start, end),
                    text.rfind('?', start, end),
                    text.rfind('!', start, end)
                )
                if last_period != -1:
                    end = last_period + 1
            
            # 添加文本块
            chunk = text[start:end].strip()
            if chunk:  # 只添加非空块
                chunks.append(chunk)
            
            # 移动到下一个起始位置，考虑重叠
            start = end - self.chunk_overlap
        
        return chunks

    def search_similar(
        self,
        query: str,
        k: int = 5,
        document_id: Optional[str] = None
    ) -> List[str]:
        """搜索相似文本块"""
        return self.vector_store.similarity_search(query, k, document_id)

    def delete_document(self, document_id: str):
        """删除文档相关的所有向量"""
        self.vector_store.delete_by_document_id(document_id)
