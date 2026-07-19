from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    problem: str
    explanation: str
    confidence: int
    commands: list[str]
