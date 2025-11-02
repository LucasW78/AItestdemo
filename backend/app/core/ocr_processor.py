"""
OCR (Optical Character Recognition) processor for image text extraction.
"""
import logging
import io
from typing import Optional, Dict, Any
from PIL import Image
import pytesseract

from app.config import settings

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Advanced OCR processing with multiple languages and preprocessing.
    """

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'chi_sim': '简体中文',
        'chi_tra': '繁体中文',
        'eng': '英文',
        'jpn': '日文',
        'kor': '韩文'
    }

    def __init__(self):
        """Initialize OCR processor with configuration."""
        # Set Tesseract command path if specified
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        # Default language configuration
        self.default_languages = ['chi_sim', 'eng']  # Chinese Simplified + English

    def extract_text_from_image(
        self,
        image: Image.Image,
        languages: Optional[list] = None,
        preprocess: bool = True,
        config: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text from PIL Image with advanced options.

        Args:
            image: PIL Image object
            languages: List of language codes
            preprocess: Whether to apply image preprocessing
            config: Custom Tesseract configuration

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Use default languages if not specified
            if not languages:
                languages = self.default_languages

            # Preprocess image if requested
            if preprocess:
                image = self._preprocess_image(image)

            # Build language string
            lang_string = '+'.join(languages)

            # Default Tesseract configuration
            default_config = '--oem 3 --psm 6'
            if config:
                final_config = f"{default_config} {config}"
            else:
                final_config = default_config

            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(
                image,
                lang=lang_string,
                config=final_config
            )

            # Get additional data (bounding boxes, confidence, etc.)
            data = pytesseract.image_to_data(
                image,
                lang=lang_string,
                config=final_config,
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Extract words with positions
            words_with_positions = []
            for i in range(len(data['text'])):
                if data['text'][i].strip() and int(data['conf'][i]) > 0:
                    words_with_positions.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })

            return {
                'text': extracted_text.strip(),
                'confidence': avg_confidence,
                'languages': languages,
                'words': words_with_positions,
                'word_count': len(words_with_positions),
                'preprocessed': preprocess
            }

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return {
                'text': '',
                'confidence': 0,
                'languages': languages or [],
                'words': [],
                'word_count': 0,
                'preprocessed': preprocess,
                'error': str(e)
            }

    def extract_text_from_bytes(
        self,
        image_bytes: bytes,
        languages: Optional[list] = None,
        preprocess: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from image bytes.

        Args:
            image_bytes: Raw image data
            languages: List of language codes
            preprocess: Whether to apply image preprocessing

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            return self.extract_text_from_image(image, languages, preprocess)
        except Exception as e:
            logger.error(f"Error processing image bytes: {e}")
            return {
                'text': '',
                'confidence': 0,
                'languages': languages or [],
                'words': [],
                'word_count': 0,
                'preprocessed': preprocess,
                'error': str(e)
            }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply image preprocessing to improve OCR accuracy.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')

            # Apply additional preprocessing techniques
            # 1. Resize if too small (improves OCR for small images)
            width, height = image.size
            if width < 300 or height < 300:
                scale_factor = max(300 / width, 300 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 2. Apply thresholding to improve contrast
            # This is a simple thresholding - more advanced methods could be added
            from PIL import ImageEnhance
            import numpy as np

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Convert to numpy array for thresholding
            img_array = np.array(image)

            # Apply adaptive thresholding
            threshold = np.mean(img_array)
            img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)

            # Convert back to PIL Image
            image = Image.fromarray(img_array)

            return image

        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return image

    def detect_languages(self, image: Image.Image) -> list:
        """
        Detect languages present in the image.

        Args:
            image: PIL Image object

        Returns:
            List of detected language codes
        """
        try:
            # This is a simplified language detection
            # In a production system, you might want to use more sophisticated methods

            # Test with different languages and see which gives the best confidence
            language_scores = {}

            for lang_code in ['chi_sim', 'chi_tra', 'eng', 'jpn', 'kor']:
                try:
                    result = self.extract_text_from_image(
                        image,
                        languages=[lang_code],
                        preprocess=True,
                        config='--psm 6'  # Simple page segmentation
                    )
                    language_scores[lang_code] = result['confidence']
                except:
                    continue

            # Sort languages by confidence
            sorted_languages = sorted(
                language_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            # Return languages with reasonable confidence (threshold: 30)
            detected_languages = [
                lang for lang, confidence in sorted_languages
                if confidence > 30
            ]

            return detected_languages if detected_languages else self.default_languages

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self.default_languages

    def extract_structured_text(
        self,
        image: Image.Image,
        languages: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Extract text with structural information (paragraphs, lines, etc.).

        Args:
            image: PIL Image object
            languages: List of language codes

        Returns:
            Dictionary with structured text data
        """
        try:
            if not languages:
                languages = self.default_languages

            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                lang='+'.join(languages),
                config='--oem 3 --psm 6',
                output_type=pytesseract.Output.DICT
            )

            # Group words into lines and paragraphs
            lines = []
            current_line = []
            last_y = -1
            line_height_threshold = 10  # Pixels threshold for same line

            for i in range(len(data['text'])):
                if data['text'][i].strip() and int(data['conf'][i]) > 0:
                    word_y = data['top'][i]

                    # Check if this word is on the same line
                    if last_y != -1 and abs(word_y - last_y) < line_height_threshold:
                        current_line.append({
                            'text': data['text'][i],
                            'confidence': int(data['conf'][i]),
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        })
                    else:
                        # Add previous line to lines list
                        if current_line:
                            lines.append(current_line)

                        # Start new line
                        current_line = [{
                            'text': data['text'][i],
                            'confidence': int(data['conf'][i]),
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }]

                    last_y = word_y

            # Add the last line
            if current_line:
                lines.append(current_line)

            # Group lines into paragraphs
            paragraphs = []
            current_paragraph = []
            last_line_bottom = -1
            paragraph_threshold = 30  # Pixels threshold for same paragraph

            for line in lines:
                if line:  # Skip empty lines
                    line_bottom = max(word['y'] + word['height'] for word in line)

                    if last_line_bottom != -1 and (line_bottom - last_line_bottom) < paragraph_threshold:
                        current_paragraph.append(line)
                    else:
                        if current_paragraph:
                            paragraphs.append(current_paragraph)
                        current_paragraph = [line]

                    last_line_bottom = line_bottom

            # Add the last paragraph
            if current_paragraph:
                paragraphs.append(current_paragraph)

            # Generate full text
            full_text = '\n\n'.join([
                '\n'.join([' '.join(word['text'] for word in line) for line in paragraph])
                for paragraph in paragraphs
            ])

            return {
                'text': full_text,
                'paragraphs': paragraphs,
                'line_count': len(lines),
                'paragraph_count': len(paragraphs),
                'languages': languages
            }

        except Exception as e:
            logger.error(f"Structured text extraction failed: {e}")
            return {
                'text': '',
                'paragraphs': [],
                'line_count': 0,
                'paragraph_count': 0,
                'languages': languages or [],
                'error': str(e)
            }

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """
        Get dictionary of supported languages.

        Returns:
            Dictionary mapping language codes to language names
        """
        return OCRProcessor.SUPPORTED_LANGUAGES.copy()

    @staticmethod
    def validate_languages(language_codes: list) -> list:
        """
        Validate and filter language codes.

        Args:
            language_codes: List of language codes to validate

        Returns:
            List of valid language codes
        """
        supported = OCRProcessor.SUPPORTED_LANGUAGES.keys()
        return [code for code in language_codes if code in supported]