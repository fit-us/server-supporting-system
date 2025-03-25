from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CBTBotResponse(BaseModel):
    cbt_category: Optional[str] = Field(None, alias="cbtCategory")
    consultation_stage: Optional[str] = Field(None, alias="consultationStage")
    triggering_situation: Optional[str] = Field(None, alias="triggeringSituation")
    automatic_thoughts: Optional[str] = Field(None, alias="automaticThoughts")
    emotions: List[str] = Field(default_factory=list)
    intensity_of_emotion: Dict[str, int] = Field(default_factory=dict, alias="intensityOfEmotion")
    underlying_beliefs: Optional[str] = Field(None, alias="underlyingBeliefs")
    cbt_question: List[str] = Field(default_factory=list, alias="cbtQuestion")
    user_response: Optional[str] = Field(None, alias="userResponse")
    therapist_notes: Optional[str] = Field(None, alias="therapistNotes")
    default_response: Optional[str] = Field(None, alias="defaultResponse")