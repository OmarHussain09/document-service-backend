import os
import tempfile
import ocrmypdf
import base64
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "Empty")
LANG = "eng"  # e.g. 'eng+hin' for English+Hindi

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "ocr_output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=GOOGLE_API_KEY
)

prompt = PromptTemplate(
    input_variables=["context"],
    template="Summarize the following text into 2–3 concise sentences:\n\n{context}"
)

def extract_text_and_summarize(input_pdf_path: str) -> str:
    # Build fixed output path based on input filename
    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
    output_pdf_path = os.path.join(OUTPUT_DIR, f"{base_name}_ocr.pdf")

    # OCR step
    ocrmypdf.ocr(
        input_pdf_path,
        output_pdf_path,
        language=LANG,
        deskew=True,
        optimize=0,
        progress_bar=False,
        force_ocr=True
    )

    # Extract text
    reader = PdfReader(output_pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Summarize with LLM
    chain = prompt | llm
    response = chain.invoke({"context": text})
    return response.content


def summarize_file(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_text_and_summarize(file_path)

    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        message = HumanMessage(
            content=[
                {"type": "text", "text": "Summarize the key content of this image in 2–3 sentences."},
                {"type": "image_url", "image_url": f"data:image/{ext.lstrip('.')};base64,{encoded}"},
            ]
        )
        response = llm.invoke([message])
        return response.content

    else:
        raise ValueError(f"Unsupported file type: {ext}")