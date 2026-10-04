"""Strict cleaned-code domains derived from the authoritative CSV dictionary."""
import csv,json
from typing import Annotated
from pydantic import BaseModel,ConfigDict,Field,Strict,AfterValidator,create_model,model_validator
from .constants import ROOT,FEATURES

with (ROOT/'data/processed/data_dictionary.csv').open(encoding='utf-8',newline='') as handle:
    DICTIONARY={r['clean_variable']:r for r in csv.DictReader(handle)}
DOMAINS={f:tuple(sorted({v for v in json.loads(DICTIONARY[f]['clean_mapping']).values() if isinstance(v,(int,float))})) for f in FEATURES if f!='bmi'}

def category_validator(feature):
    def validate(value):
        if value not in DOMAINS[feature]:raise ValueError('Unsupported cleaned category')
        return value
    return validate

class ProfileBase(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,allow_inf_nan=False)
    @model_validator(mode='before')
    @classmethod
    def require_named_record(cls,value):
        if not isinstance(value,dict) or not value:raise ValueError('Provide a nonempty named profile; null values are allowed')
        return value

fields={}
for feature in FEATURES:
    if feature=='bmi':annotation=Annotated[float,Strict(),Field(ge=12,le=99.99)]
    else:annotation=Annotated[int,Strict(),AfterValidator(category_validator(feature))]
    fields[feature]=(annotation|None,Field(default=None,description=DICTIONARY[feature]['description'],json_schema_extra={} if feature=='bmi' else {'enum':[*DOMAINS[feature],None]}))
HealthProfile=create_model('HealthProfile',__base__=ProfileBase,**fields)

def validate_profile(value):return HealthProfile.model_validate(value).model_dump()
