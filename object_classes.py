from dataclasses import dataclass
    
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