from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=12000)
    dates: str = Field(..., min_length=2, max_length=300)
    language: str = Field(default="English", min_length=2, max_length=50)

    @field_validator("document_type", "parties", "terms", "dates", "language")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    generated_by: str = "LegalEase AI"


class ExportRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=1, max_length=100000)
