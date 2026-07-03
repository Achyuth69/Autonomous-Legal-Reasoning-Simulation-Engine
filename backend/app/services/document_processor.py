import os
from typing import Optional, Dict, Any
import aiofiles
from pathlib import Path
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
from io import BytesIO
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Process and extract text from various document formats"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, filename: str, content: bytes) -> str:
        """Save uploaded file and return path"""
        file_path = self.upload_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Saved file: {filename}")
        return str(file_path)
    
    async def extract_text(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract text from document based on file type"""
        try:
            if file_type == "pdf":
                return await self._extract_from_pdf(file_path)
            elif file_type == "docx":
                return await self._extract_from_docx(file_path)
            elif file_type == "txt":
                return await self._extract_from_txt(file_path)
            elif file_type in ["png", "jpg", "jpeg"]:
                return await self._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {
                "text": "",
                "page_count": 0,
                "error": str(e)
            }
    
    async def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        text = ""
        page_count = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
        
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            # If standard extraction fails, could try OCR as fallback
        
        return {
            "text": text.strip(),
            "page_count": page_count,
            "method": "pdf_extract"
        }
    
    async def _extract_from_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX"""
        text = ""
        
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            text = "\n\n".join(paragraphs)
        
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
        
        return {
            "text": text.strip(),
            "page_count": 1,  # DOCX doesn't have clear pages
            "method": "docx_extract"
        }
    
    async def _extract_from_txt(self, file_path: str) -> Dict[str, Any]:
        """Extract text from TXT"""
        text = ""
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                text = await f.read()
        
        except Exception as e:
            logger.error(f"TXT extraction error: {str(e)}")
        
        return {
            "text": text.strip(),
            "page_count": 1,
            "method": "txt_extract"
        }
    
    async def _extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        text = ""
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
        
        return {
            "text": text.strip(),
            "page_count": 1,
            "method": "ocr_extract"
        }
    
    def cleanup_old_files(self, days: int = 7):
        """Remove files older than specified days"""
        import time
        current_time = time.time()
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (days * 86400):  # days to seconds
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path.name}")
