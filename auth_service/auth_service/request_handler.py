"""TODO"""
import datetime as dt
from pydantic  import BaseModel, Field, field_validator, StrictStr
from typing import Optional
from .local_constants import (
    GRANT_TYPES,
    RESPONSE_TYPES, 
    TOKEN_ENDPOINT_METHOD
)


class RegisterHandler(BaseModel):
    """TODO"""
    username: str = Field(..., min_length=1, description='Username of the user.')
    password: str = Field(..., min_length=1, description='Password of the user.')
    name: str = Field(..., min_length=1, description='Family name of the user.')
    first_name: str = Field(..., min_length=1, description='First name of the user.')
    email: str = Field(..., min_length=1, description='Email of the user.')
    telephone_num: Optional[str] = Field(default=None, description='Telephone number of the user. Optional.')
    birthday: Optional[dt.datetime] = Field(default=None, description='Birthday of the user. Optional.')
    nationality: Optional[str] = Field(default=None, description='Nationality of the user. Optional.')
    address: Optional[str] = Field(default=None, description='Address of the user. Optional.')
    
    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, value: str) -> str:
        """TODO"""
        return value
    
    @field_validator('email', mode='after')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """TODO"""
        return value
    
    @field_validator('birthday', mode='before')
    @classmethod
    def validate_birthday(cls, value: str | dt.datetime): 
        """TODO"""  
        if isinstance(value, str):
            value = dt.datetime.strptime(value, "%Y-%m-%d")
        return value
    
def split_by_crlf(s: str) -> list[str]: 
    return [v for v in s.splitlines() if v]

class CreateClientHandler(BaseModel):
    """TODO"""
    client_name: str = Field(..., min_length=1, description='Name of the client')
    client_uri: str = Field(..., description='URI of the client')
    grant_types:list[str] = Field(..., description=r'Grant types of the client. Seperated by \n')
    response_types: list[str] = Field(..., description=r'Response types of the client. Seperated by \n')
    redirect_uris: list[str] = Field(..., description=r'Redirect URIs of the client. Seperated by \n')
    scope: str = Field(..., description=r'Scopes of the client. Seperated by \s.')
    token_endpoint_auth_method: str = Field(..., description='Token endpoint methods of the client')

    @field_validator('grant_types', 'response_types', 'redirect_uris', mode='before')
    @classmethod
    def check_new_line_seperated_fields(cls, value: str | list[str]) -> list[str]:
        """TODO"""
        if isinstance(value, str):
            value = split_by_crlf(value)
        return value

    @field_validator('grant_types', mode='after')
    @classmethod
    def validate_grant_types(cls, values: list[str]) -> list[str]:
        """TODO"""
        for v in values:
            if v not in GRANT_TYPES:
                raise ValueError(f'Grant type: {v} not in supported grant types: {GRANT_TYPES}')
        return values
    
    @field_validator('response_types', mode='after')
    @classmethod
    def validate_response_types(cls, values: list[str]) -> list[str]:
        """TODO"""
        for v in values:
            if v not in RESPONSE_TYPES:
                raise ValueError(f'Response type: {v} not in supported response types: {RESPONSE_TYPES}')
        return values
    
    @field_validator('scope', mode='after')
    @classmethod
    def validate_scope(cls, values: str) -> str:
        """TODO"""
        return values
    
    @field_validator('token_endpoint_auth_method', mode='after')
    @classmethod
    def validate_token_endpoint_auth_method(cls, value: str) -> str:
        """TODO"""
        if value not in TOKEN_ENDPOINT_METHOD:
            raise ValueError(f'Token endpoint method: {value} not in supported token endpoint methods: {TOKEN_ENDPOINT_METHOD}')    
        return value
        