from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    hook_text: str
