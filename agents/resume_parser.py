import io
import zipfile
import xml.etree.ElementTree as ET
import PyPDF2

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF file in bytes format using PyPDF2.
    """
    text = ""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text.strip()

def extract_text_from_docx(docx_bytes: bytes) -> str:
    """
    Extracts text from a DOCX file in bytes format using python's built-in zipfile and XML parser.
    This avoids external dependencies like docx2txt.
    """
    try:
        docx_file = io.BytesIO(docx_bytes)
        with zipfile.ZipFile(docx_file) as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            # Find all text elements under wordprocessingml namespace
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            text_elems = root.findall('.//w:t', namespaces)
            return "".join([elem.text for elem in text_elems if elem.text]).strip()
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""

def extract_resume_text(file_name: str, file_bytes: bytes) -> str:
    """
    Extracts text based on the file extension.
    """
    ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
    if ext == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif ext in ['docx', 'doc']:
        return extract_text_from_docx(file_bytes)
    elif ext == 'txt':
        try:
            return file_bytes.decode('utf-8')
        except Exception:
            try:
                return file_bytes.decode('latin-1')
            except Exception:
                return ""
    else:
        return ""
