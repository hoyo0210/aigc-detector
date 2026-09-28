from pydantic import BaseModel, Field

# 最小文本长度限制
MIN_TEXT_LENGTH = 500

class DetectRequest(BaseModel):
    text: str = Field(..., min_length=MIN_TEXT_LENGTH, max_length=8000, description=f"文本内容，至少需要{MIN_TEXT_LENGTH}字")

class DetectResult(BaseModel):
    label: str  # human | ai | uncertain
    score: float
    confidence: str  # high | medium | low
    rationale: str
    detailed_analysis: str
    key_indicators: list[str]
    methodology: str

class DetectResponse(BaseModel):
    result: DetectResult
