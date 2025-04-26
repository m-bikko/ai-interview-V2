import os
import PyPDF2
import logging
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class CVService:
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            The extracted text as a string
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            if not text.strip():
                logger.warning(f"No text extracted from PDF: {pdf_path}")
                return "No readable text found in the CV. The PDF might be scanned or contain images."
            
            logger.info(f"Successfully extracted text from PDF: {pdf_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"Error processing PDF: {str(e)}"
    
    def process_cv(self, pdf_path):
        """
        Process a CV by extracting text and generating a review.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            The generated review as a string
        """
        try:
            # Extract text from PDF
            cv_text = self.extract_text_from_pdf(pdf_path)
            
            # If no text could be extracted
            if cv_text.startswith("Error") or cv_text.startswith("No readable"):
                return cv_text
            
            # Generate review using Gemini API
            review = self.gemini_service.review_cv(cv_text)
            
            return review
            
        except Exception as e:
            logger.error(f"Error processing CV: {e}")
            return f"Error processing CV: {str(e)}"