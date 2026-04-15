"""
Docling Service - Document parsing API
Provides PDF/DOCX/PPTX to Markdown conversion using Docling
"""
import os
import tempfile
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    PowerpointFormatOption,
    WordFormatOption,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

app = FastAPI(title="Docling Service", description="Document parsing service using Docling")


class ParseRequest(BaseModel):
    file_path: str


class ParseResponse(BaseModel):
    success: bool
    markdown: str | None = None
    error: str | None = None


# Initialize Docling converter at startup
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False

converter = DocumentConverter(
    allowed_formats=[InputFormat.PPTX, InputFormat.PDF, InputFormat.DOCX],
    format_options={
        InputFormat.DOCX: WordFormatOption(pipeline_options=pipeline_options),
        InputFormat.PPTX: PowerpointFormatOption(pipeline_options=pipeline_options),
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
    },
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docling-service"}


@app.post("/parse", response_model=ParseResponse)
async def parse_document(file_path: str):
    """
    Parse a document (PDF/DOCX/PPTX) to Markdown

    Args:
        file_path: Path to the document file

    Returns:
        Markdown content of the document
    """
    if not os.path.exists(file_path):
        return ParseResponse(
            success=False,
            error=f"File not found: {file_path}"
        )

    try:
        result = converter.convert(file_path)
        markdown = result.document.export_to_markdown()
        return ParseResponse(success=True, markdown=markdown)
    except Exception as e:
        return ParseResponse(
            success=False,
            error=str(e)
        )


@app.post("/parse/upload")
async def parse_uploaded_document(file: UploadFile = File(...)):
    """
    Parse an uploaded document (PDF/DOCX/PPTX) to Markdown

    Args:
        file: Uploaded document file

    Returns:
        Markdown content of the document
    """
    allowed_content_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: {allowed_content_types}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        try:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

            result = converter.convert(tmp_path)
            markdown = result.document.export_to_markdown()

            return JSONResponse(content={
                "success": True,
                "markdown": markdown,
                "filename": file.filename
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
