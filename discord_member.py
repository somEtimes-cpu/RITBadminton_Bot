from dataclasses import dataclass

@dataclass
class Discord_Member:
    '''Class for recording registered discord member'''
    Discord_ID: int
    Discrod_Name: str
    is_RIT: str
    First_name: str
    Last_name: str
    Email: str
    pronoun: str
    is_Eboard: str
    is_Former_Eboard: str