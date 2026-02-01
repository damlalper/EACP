"""
Vision Agent for EACP
Handles PDF, diagrams, tables, and image understanding
"""

from typing import Dict, List, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Optional imports for real OCR/PDF processing
try:
    import easyocr
except ImportError:
    easyocr = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PIL import Image
except ImportError:
    Image = None


class VisionAgent:
    """Agent for vision and document understanding using EasyOCR and pdfplumber."""
    
    def __init__(self, llm_client=None, ocr_languages: List[str] = None):
        self.llm_client = llm_client
        self.ocr_engine = None
        self.ocr_languages = ocr_languages or ['en']
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize OCR engine (EasyOCR if available, else mock)."""
        try:
            if easyocr:
                self.ocr_engine = easyocr.Reader(self.ocr_languages)
                logger.info(f"EasyOCR engine initialized with languages: {self.ocr_languages}")
            else:
                logger.warning("easyocr not installed; falling back to mock OCR")
                self.ocr_engine = "mock"
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}; falling back to mock")
            self.ocr_engine = "mock"
    
    def process_image(self, image_path: str, task: str = "describe") -> Dict[str, Any]:
        """
        Process an image
        Tasks: describe, extract_text, extract_table, analyze_diagram
        """
        try:
            if task == "extract_text":
                return self._extract_text(image_path)
            elif task == "extract_table":
                return self._extract_table(image_path)
            elif task == "analyze_diagram":
                return self._analyze_diagram(image_path)
            else:
                return self._describe_image(image_path)
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return {"error": str(e)}
    
    def process_pdf(self, pdf_path: str, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """Process a PDF document"""
        try:
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_path, pages)
            
            # Extract tables if any
            tables = self._extract_pdf_tables(pdf_path, pages)
            
            # Generate summary if LLM available
            summary = None
            if self.llm_client:
                summary = self._generate_summary(text_content)
            
            return {
                "pdf_path": pdf_path,
                "text_content": text_content,
                "tables": tables,
                "summary": summary,
                "page_count": len(pages) if pages else "all"
            }
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {"error": str(e)}
    
    def _extract_text(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image using OCR (EasyOCR or mock)."""
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}"}
        
        if easyocr and isinstance(self.ocr_engine, easyocr.Reader):
            try:
                result = self.ocr_engine.readtext(image_path)
                text = "\n".join([detection[1] for detection in result])
                confidence = sum([detection[2] for detection in result]) / len(result) if result else 0.0
                return {
                    "image_path": image_path,
                    "text": text,
                    "confidence": confidence,
                    "detections": len(result)
                }
            except Exception as e:
                logger.error(f"EasyOCR extraction failed: {str(e)}")
                return {"error": str(e)}
        
        # Mock fallback
        return {
            "image_path": image_path,
            "text": "[Mock OCR text extraction]",
            "confidence": 0.85
        }
    
    def _extract_table(self, image_path: str) -> Dict[str, Any]:
        """Extract table from image"""
        return {
            "image_path": image_path,
            "table_data": [],
            "format": "csv"
        }
    
    def _analyze_diagram(self, image_path: str) -> Dict[str, Any]:
        """Analyze diagram and extract structure"""
        if self.llm_client:
            # Use vision-capable LLM to analyze diagram
            prompt = f"Analyze this diagram from {image_path} and describe its structure and components."
            description = self.llm_client.generate(prompt=prompt)
            return {
                "image_path": image_path,
                "description": description,
                "components": []
            }
        
        return {
            "image_path": image_path,
            "description": "[Mock diagram analysis]",
            "components": []
        }
    
    def _describe_image(self, image_path: str) -> Dict[str, Any]:
        """Generate description of image"""
        if self.llm_client:
            prompt = f"Describe the contents of this image: {image_path}"
            description = self.llm_client.generate(prompt=prompt)
            return {
                "image_path": image_path,
                "description": description
            }
        
        return {
            "image_path": image_path,
            "description": "[Mock image description]"
        }
    
    def _extract_pdf_text(self, pdf_path: str, pages: Optional[List[int]]) -> str:
        """Extract text from PDF using pdfplumber or fallback to mock."""
        if not os.path.exists(pdf_path):
            return f"[PDF file not found: {pdf_path}]"
        
        if pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    text_parts = []
                    page_list = pages if pages else range(len(pdf.pages))
                    for page_num in page_list:
                        if page_num < len(pdf.pages):
                            page = pdf.pages[page_num]
                            text = page.extract_text()
                            if text:
                                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                    return "\n\n".join(text_parts)
            except Exception as e:
                logger.error(f"pdfplumber extraction failed: {str(e)}")
                return f"[PDF extraction error: {str(e)}]"
        
        # Mock fallback
        return "[Mock PDF text extraction]"
    
    def _extract_pdf_tables(self, pdf_path: str, pages: Optional[List[int]]) -> List[Dict]:
        """Extract tables from PDF"""
        return []
    
    def _generate_summary(self, text: str) -> str:
        """Generate summary of extracted text"""
        if self.llm_client:
            prompt = f"Summarize the following document:\n\n{text[:1000]}"
            return self.llm_client.generate(prompt=prompt)
        return "[Mock summary]"
