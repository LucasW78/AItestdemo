"""
File processing utilities for different file types.
"""
import os
import logging
from pathlib import Path
from typing import Optional, BinaryIO
import asyncio
from io import BytesIO

# File processing libraries
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
from pdf2image import convert_from_bytes

from app.config import settings

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Utility class for processing different file types.
    """

    # Supported file types
    SUPPORTED_TEXT_TYPES = ['.txt']
    SUPPORTED_PDF_TYPES = ['.pdf']
    SUPPORTED_EXCEL_TYPES = ['.xls', '.xlsx']
    SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    @classmethod
    def get_file_type(cls, filename: str) -> str:
        """
        Determine file type from filename.
        """
        ext = Path(filename).suffix.lower()

        if ext in cls.SUPPORTED_TEXT_TYPES:
            return 'text'
        elif ext in cls.SUPPORTED_PDF_TYPES:
            return 'pdf'
        elif ext in cls.SUPPORTED_EXCEL_TYPES:
            return 'excel'
        elif ext in cls.SUPPORTED_IMAGE_TYPES:
            return 'image'
        else:
            return 'unknown'

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """
        Check if file type is supported.
        """
        file_type = cls.get_file_type(filename)
        return file_type != 'unknown'

    @classmethod
    async def extract_text(cls, file_path: str, file_type: Optional[str] = None) -> str:
        """
        Extract text from a file based on its type.
        """
        if not file_type:
            file_type = cls.get_file_type(file_path)

        try:
            if file_type == 'text':
                return await cls._extract_from_text(file_path)
            elif file_type == 'pdf':
                return await cls._extract_from_pdf(file_path)
            elif file_type == 'excel':
                return await cls._extract_from_excel(file_path)
            elif file_type == 'image':
                return await cls._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    @classmethod
    async def _extract_from_text(cls, file_path: str) -> str:
        """
        Extract text from plain text files.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read()
            except:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()

    @classmethod
    async def _extract_from_pdf(cls, file_path: str) -> str:
        """
        Extract text from PDF files using pdfplumber.
        """
        text_content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue

            return '\n\n'.join(text_content) if text_content else ""
        except Exception as e:
            logger.error(f"Error processing PDF with pdfplumber: {e}")
            # Fallback to OCR
            return await cls._extract_from_pdf_ocr(file_path)

    @classmethod
    async def _extract_from_pdf_ocr(cls, file_path: str) -> str:
        """
        Extract text from PDF files using OCR.
        """
        try:
            images = convert_from_bytes(open(file_path, 'rb').read())
            text_content = []

            for page_num, image in enumerate(images):
                try:
                    # Configure Tesseract for better OCR
                    custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
                    page_text = pytesseract.image_to_string(image, config=custom_config)
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num + 1} (OCR) ---\n{page_text}")
                except Exception as e:
                    logger.warning(f"Error OCR processing page {page_num + 1}: {e}")
                    continue

            return '\n\n'.join(text_content) if text_content else ""
        except Exception as e:
            logger.error(f"Error with PDF OCR: {e}")
            return ""

    @classmethod
    async def _extract_from_excel(cls, file_path: str) -> str:
        """
        Extract text from Excel files.
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=None)

            text_content = []
            for sheet_name, sheet_df in df.items():
                text_content.append(f"--- Sheet: {sheet_name} ---")

                # Convert DataFrame to string
                sheet_text = sheet_df.to_string(index=False, na_rep='')
                text_content.append(sheet_text)

            return '\n\n'.join(text_content) if text_content else ""
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return ""

    @classmethod
    async def _extract_from_image(cls, file_path: str) -> str:
        """
        Extract text from image files using OCR.
        """
        try:
            # Open image
            image = Image.open(file_path)

            # Configure Tesseract for better OCR (supports Chinese and English)
            custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'

            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)

            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return ""

    @classmethod
    async def process_uploaded_file(cls, file_content: bytes, filename: str) -> dict:
        """
        Process uploaded file content directly from memory.
        """
        file_type = cls.get_file_type(filename)

        if file_type == 'unknown':
            raise ValueError(f"Unsupported file type: {filename}")

        try:
            if file_type == 'text':
                # Decode text content
                try:
                    text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = file_content.decode('gbk')
                    except:
                        text = file_content.decode('latin-1')
                return {"text": text, "type": file_type}

            elif file_type == 'image':
                # Process image with OCR
                image = Image.open(BytesIO(file_content))
                custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
                text = pytesseract.image_to_string(image, config=custom_config)
                return {"text": text.strip(), "type": file_type}

            elif file_type == 'pdf':
                # Process PDF with pdfplumber
                text_content = []
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                        except:
                            continue

                text = '\n\n'.join(text_content) if text_content else ""

                # If no text extracted, try OCR
                if not text.strip():
                    images = convert_from_bytes(file_content)
                    for page_num, image in enumerate(images):
                        try:
                            custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
                            page_text = pytesseract.image_to_string(image, config=custom_config)
                            if page_text.strip():
                                text_content.append(f"--- Page {page_num + 1} (OCR) ---\n{page_text}")
                        except:
                            continue
                    text = '\n\n'.join(text_content) if text_content else ""

                return {"text": text, "type": file_type}

            elif file_type == 'excel':
                # Process Excel file
                df = pd.read_excel(BytesIO(file_content), sheet_name=None)
                text_content = []
                for sheet_name, sheet_df in df.items():
                    text_content.append(f"--- Sheet: {sheet_name} ---")
                    sheet_text = sheet_df.to_string(index=False, na_rep='')
                    text_content.append(sheet_text)

                text = '\n\n'.join(text_content) if text_content else ""
                return {"text": text, "type": file_type}

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            logger.error(f"Error processing uploaded file {filename}: {e}")
            raise

    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate file before upload.
        """
        # Check file type
        if not cls.is_supported(filename):
            return False, f"Unsupported file type. Supported types: {', '.join(cls.get_supported_extensions())}"

        # Check file size
        max_size = settings.max_file_size
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_size_mb:.1f}MB"

        return True, "File is valid"

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.
        """
        return (
            cls.SUPPORTED_TEXT_TYPES +
            cls.SUPPORTED_PDF_TYPES +
            cls.SUPPORTED_EXCEL_TYPES +
            cls.SUPPORTED_IMAGE_TYPES
        )