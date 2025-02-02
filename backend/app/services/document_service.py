import io
import os
import PyPDF2
import docx2txt
from fastapi import UploadFile
from datetime import datetime

class DocumentProcessingService:
    def __init__(self):
        self.upload_dir = "documents"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_and_process(self, file: UploadFile):
        """
        保存文件并提取文本
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(self.upload_dir, filename)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return self.extract_text(content, file.filename), filename

    def extract_text(self, content: bytes, filename: str):
        """
        从不同类型文档中提取文本
        """
        filename = filename.lower()
        
        if filename.endswith('.pdf'):
            return self._extract_pdf_text(content)
        elif filename.endswith('.docx'):
            return self._extract_docx_text(content)
        elif filename.endswith('.txt'):
            return content.decode('utf-8')
        else:
            raise ValueError("不支持的文件类型")

    def _extract_pdf_text(self, content):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def _extract_docx_text(self, content):
        return docx2txt.process(io.BytesIO(content))
