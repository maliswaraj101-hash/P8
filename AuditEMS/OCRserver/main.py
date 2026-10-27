from mcp.server.fastmcp import FastMCP
import pytesseract
from PIL import Image
import io
import filetype
import fitz  # PyMuPDF
import pandas as pd
from docx import Document

import base64

mcp = FastMCP(name = "OCRserver")

@mcp.tool()
def ocr(file_base64: str) -> str :
    """Extract text from various file formats (Images, PDF, Excel, Word). Input should be base64 encoded."""
    try:
        file = base64.b64decode(file_base64)
    except Exception as e:
        return f"Error: Invalid base64 data ({str(e)})"
        
    kind = filetype.guess(file)
    content = ""
    
    if kind is None:
        # Fallback to image OCR if detection fails but it might be an image
        try:
            image = Image.open(io.BytesIO(file))
            return pytesseract.image_to_string(image).strip()
        except Exception:
            return "Error: Unsupported or unknown file format."

    mime = kind.mime
    
    try:
        if mime.startswith("image/"):
            image = Image.open(io.BytesIO(file))
            content = pytesseract.image_to_string(image)
            
        elif mime == "application/pdf":
            doc = fitz.open(stream=file, filetype="pdf")
            text_blocks = []
            for page in doc:
                text_blocks.append(page.get_text())
            content = "\n".join(text_blocks)
            doc.close()
            
        elif mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or mime == "application/vnd.ms-excel":
            df_dict = pd.read_excel(io.BytesIO(file), sheet_name=None)
            sheets_content = []
            for sheet_name, df in df_dict.items():
                sheets_content.append(f"--- Sheet: {sheet_name} ---\n{df.to_string(index=False)}")
            content = "\n\n".join(sheets_content)
            
        elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(io.BytesIO(file))
            content = "\n".join([para.text for para in doc.paragraphs])
            
        elif mime == "text/plain":
            content = file.decode("latin-1", errors="ignore")
            
        else:
            return f"Error: Unsupported file type ({mime})"
            
    except Exception as e:
        return f"Error processing file: {str(e)}"

    return content.strip()


if __name__ == "__main__":
    mcp.run()
