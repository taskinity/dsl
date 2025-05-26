"""
Local OCR Processing Module

This module provides local OCR processing capabilities without requiring external API calls.
Uses Tesseract OCR for text extraction from images and PDFs.
"""
import os
import io
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, BinaryIO

import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

class LocalOCRProcessor:
    """Local OCR processor using Tesseract OCR."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the local OCR processor.
        
        Args:
            config: Configuration dictionary with OCR settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Set Tesseract command if specified
        if 'tesseract_cmd' in self.config:
            pytesseract.pytesseract.tesseract_cmd = self.config['tesseract_cmd']
        
        # Default configuration
        self.languages = self.config.get('languages', ['eng'])
        self.dpi = self.config.get('dpi', 300)
        self.oem = self.config.get('oem', 1)  # 1 = LSTM + Legacy
        self.psm = self.config.get('psm', 6)  # 6 = Assume single uniform block of text
        self.use_gpu = self.config.get('use_gpu', False)
        self.max_threads = self.config.get('max_threads', 4)
        
        # Configure OpenCV threading
        cv2.setNumThreads(self.max_threads)
        
        # Set environment variables for Tesseract
        os.environ['OMP_THREAD_LIMIT'] = str(self.max_threads)
        os.environ['OMP_NUM_THREADS'] = str(self.max_threads)
        
        # Create temp directory if it doesn't exist
        self.temp_dir = Path(self.config.get('temp_dir', tempfile.mkdtemp(prefix='ocr_'))) 
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Initialized LocalOCRProcessor with config: {self.config}")
    
    def cleanup(self):
        """Clean up temporary files."""
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __del__(self):
        """Clean up on object deletion."""
        self.cleanup()
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results.
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV)
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3 and image.shape[2] == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply thresholding to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply dilation to connect text components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            
            return dilated
            
        except Exception as e:
            self.logger.warning(f"Error in image preprocessing: {e}")
            return image  # Return original if preprocessing fails
    
    def extract_text_from_image(self, image: Union[str, Path, BinaryIO, np.ndarray]) -> str:
        """Extract text from an image file or numpy array.
        
        Args:
            image: Path to image file, file-like object, or numpy array
            
        Returns:
            Extracted text as string
        """
        try:
            # Load image if it's a file path or file-like object
            if isinstance(image, (str, Path)):
                img = cv2.imread(str(image))
            elif hasattr(image, 'read'):  # File-like object
                img_array = np.frombuffer(image.read(), np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            else:  # Assume it's a numpy array
                img = image
            
            if img is None:
                raise ValueError("Could not load image")
                
            # Preprocess the image
            processed_img = self.preprocess_image(img)
            
            # Configure Tesseract parameters
            config = (
                f'--oem {self.oem} '  
                f'--psm {self.psm} '  
                f'-l "+".join({self.languages}) '  
                f'--tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata'  
            )
            
            # Run Tesseract OCR
            text = pytesseract.image_to_string(
                processed_img,
                config=config,
                output_type=pytesseract.Output.STRING
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error in text extraction: {e}", exc_info=True)
            return ""
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """Extract text from a PDF document.
        
        Args:
            pdf_data: PDF file contents as bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        result = {
            'pages': [],
            'full_text': '',
            'page_count': 0,
            'success': False
        }
        
        try:
            # Convert PDF to images
            images = convert_from_bytes(
                pdf_data,
                dpi=self.dpi,
                thread_count=self.max_threads,
                fmt='jpeg',
                output_folder=str(self.temp_dir / 'pdf_pages'),
                output_file='page',
                paths_only=True
            )
            
            # Process each page
            full_text = []
            for i, img_path in enumerate(images, 1):
                try:
                    # Extract text from page image
                    page_text = self.extract_text_from_image(img_path)
                    
                    # Add to results
                    result['pages'].append({
                        'page_number': i,
                        'text': page_text,
                        'image_path': str(img_path)
                    })
                    full_text.append(page_text)
                    
                except Exception as e:
                    self.logger.error(f"Error processing page {i}: {e}")
            
            # Combine all pages
            result['full_text'] = '\n\n'.join(full_text)
            result['page_count'] = len(images)
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error in PDF processing: {e}", exc_info=True)
            result['error'] = str(e)
        
        return result
    
    def process_file(self, file_path: Union[str, Path], file_type: str = None) -> Dict[str, Any]:
        """Process a file with the appropriate OCR method.
        
        Args:
            file_path: Path to the file to process
            file_type: Optional file type (pdf, jpg, png, etc.)
            
        Returns:
            Dictionary with processing results
        """
        file_path = Path(file_path)
        if not file_type:
            file_type = file_path.suffix.lower().lstrip('.')
        
        result = {
            'file_path': str(file_path),
            'file_type': file_type,
            'success': False,
            'text': '',
            'metadata': {}
        }
        
        try:
            if file_type.lower() == 'pdf':
                # Process PDF file
                with open(file_path, 'rb') as f:
                    pdf_result = self.extract_text_from_pdf(f.read())
                    result.update(pdf_result)
            else:
                # Process image file
                result['text'] = self.extract_text_from_image(file_path)
                result['success'] = bool(result['text'].strip())
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            result['error'] = str(e)
        
        return result

def create_ocr_processor(config: Optional[Dict[str, Any]] = None) -> LocalOCRProcessor:
    """Create a configured instance of LocalOCRProcessor.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured LocalOCRProcessor instance
    """
    return LocalOCRProcessor(config=config or {})

# Example usage
if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python local_ocr.py <path_to_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Create and configure OCR processor
    ocr_config = {
        'languages': ['eng'],
        'dpi': 300,
        'oem': 1,
        'psm': 6,
        'use_gpu': False,
        'max_threads': 4
    }
    
    processor = create_ocr_processor(ocr_config)
    
    try:
        # Process the file
        result = processor.process_file(file_path)
        
        if result.get('success', False):
            print("\n=== Extracted Text ===\n")
            print(result.get('text', 'No text extracted'))
            
            if 'pages' in result:
                print(f"\nProcessed {len(result['pages'])} pages")
        else:
            print(f"Error processing file: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        processor.cleanup()
