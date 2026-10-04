from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_serializer
from src.inference.validation import HealthProfile
ThresholdProfile=Literal['research_balanced','high_sensitivity_80','high_sensitivity_90','youden','conventional_050']

class StrictModel(BaseModel):model_config=ConfigDict(extra='forbid',strict=True,allow_inf_nan=False)
class PredictionRequest(StrictModel):
    profile:HealthProfile
    threshold_profile:ThresholdProfile='research_balanced'
class BatchRequest(StrictModel):
    profiles:list[HealthProfile]=Field(min_length=1,max_length=1000)
    threshold_profile:ThresholdProfile='research_balanced'
class PredictionResponse(StrictModel):
    profile_score:float=Field(ge=0,le=1)
    classification:Literal['lower_model_association','elevated_model_association']
    threshold:float
    threshold_profile:ThresholdProfile
    model_version:str
    model_name:str
    model_context:str
    @field_serializer('profile_score')
    def display_score(self,value):return round(value,6)
class BatchResponse(StrictModel):
    predictions:list[PredictionResponse]
    count:int
