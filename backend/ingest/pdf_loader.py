import fitz  # PyMuPDF
import os
from typing import List, Dict, Any, Tuple
import re

class PDFLoader:
    """Handles loading and processing of PDF documents."""
    
    def __init__(self):
        """Initialize the PDF Loader."""
        pass
    
    def load_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Load a PDF file and extract its text and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted text, metadata dictionary)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "page_count": len(doc),
                "file_size": os.path.getsize(file_path)
            }
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(doc):
                text = page.get_text()
                full_text += f"Page {page_num + 1}:\n{text}\n\n"
            
            return full_text, metadata
        
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")
    
    def extract_text_by_page(self, file_path: str) -> List[str]:
        """Extract text from each page of a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of strings, where each string is the text from one page
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            
            # Extract text from each page
            pages_text = []
            for page in doc:
                text = page.get_text()
                pages_text.append(text)
            
            return pages_text
        
        except Exception as e:
            raise Exception(f"Error extracting text by page: {str(e)}")
    
    def extract_images(self, file_path: str, output_dir: str) -> List[str]:
        """Extract images from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            output_dir: Directory to save extracted images
            
        Returns:
            List of paths to the extracted images
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            
            # Extract images
            image_paths = []
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]  # Get the XREF of the image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Determine image extension
                    ext = base_image["ext"]
                    
                    # Save the image
                    image_filename = f"page{page_num + 1}_img{img_index + 1}.{ext}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    image_paths.append(image_path)
            
            return image_paths
        
        except Exception as e:
            raise Exception(f"Error extracting images: {str(e)}")
    
    def extract_toc(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract the table of contents (TOC) from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries representing the TOC structure
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            
            # Extract TOC
            toc = doc.get_toc()
            
            # Convert to a more readable format
            formatted_toc = []
            for item in toc:
                level, title, page = item
                formatted_toc.append({
                    "level": level,
                    "title": title,
                    "page": page
                })
            
            return formatted_toc
        
        except Exception as e:
            raise Exception(f"Error extracting TOC: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for processing.
        
        Args:
            text: The text to split into chunks
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Clean the text by removing excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is shorter than chunk_size, return it as a single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the current chunk
            end = start + chunk_size
            
            # If we're not at the end of the text, try to find a good breaking point
            if end < len(text):
                # Try to find the last period, question mark, or exclamation point
                last_period = max(text.rfind('.', start, end), 
                                text.rfind('?', start, end),
                                text.rfind('!', start, end))
                
                # If found, break at the period
                if last_period != -1 and last_period > start + chunk_size // 2:
                    end = last_period + 1
                else:
                    # Otherwise, try to find the last space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space + 1
            
            # Add the chunk to the list
            chunks.append(text[start:end].strip())
            
            # Move the start position for the next chunk, accounting for overlap
            start = end - overlap
            if start < 0:
                start = 0
        
        return chunks