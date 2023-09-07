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
    
@dataclass
class reserved_event():
    event_name: str
    starting_hr: str
    ending_hr: str
    starting_min: str
    ending_min: str
    starting_timez: str
    ending_timez: str
    starting_px: int