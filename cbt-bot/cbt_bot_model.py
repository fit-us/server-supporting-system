from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CBTQuestion(BaseModel):
    type: str = Field(..., alias="type")  # proto의 "type" 필드와 매핑
    question: str = Field(..., alias="question")  # proto의 "question" 필드와 매핑
    choices: Optional[List[str]] = Field(None, alias="choices")

class CBTResponse(BaseModel):
    cbt_question: List[CBTQuestion] = Field(default_factory=list, alias="cbtQuestion")
    
class AnalysisResponse(BaseModel):
    cbt_category: Optional[str] = Field(None, alias="cbtCategory")
    consultation_stage: Optional[str] = Field(None, alias="consultationStage")
    triggering_situation: Optional[str] = Field(None, alias="triggeringSituation")
    automatic_thoughts: Optional[str] = Field(None, alias="automaticThoughts")
    emotions: List[str] = Field(default_factory=list)
    intensity_of_emotion: Dict[str, int] = Field(default_factory=dict, alias="intensityOfEmotion")
    underlying_beliefs: Optional[str] = Field(None, alias="underlyingBeliefs")
    user_request: Optional[str] = Field(None, alias="userRequest")
    therapist_notes: Optional[str] = Field(None, alias="therapistNotes")