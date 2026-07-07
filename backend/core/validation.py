import re

def validate_crime_no(crime_no: str) -> bool:
    """
    Validate CrimeNo per the official Karnataka Police specification:
    18 digits: 1 digit category + 4 digit district ID + 4 digit PS ID + 4 digit year + 5 digit running serial.
    """
    if not crime_no or len(crime_no) != 18 or not crime_no.isdigit():
        return False
    
    # Year part is at indices 9-12 (0-indexed, slice [9:13])
    try:
        year = int(crime_no[9:13])
    except ValueError:
        return False
        
    return 1900 <= year <= 2099

def validate_case_no(case_no: str) -> bool:
    """
    Validate CaseNo per the official Karnataka Police specification:
    9 digits: 4 digit year + 5 digit running serial.
    """
    if not case_no or len(case_no) != 9 or not case_no.isdigit():
        return False
        
    # Year part is at indices 0-3
    try:
        year = int(case_no[:4])
    except ValueError:
        return False
        
    return 1900 <= year <= 2099

def generate_crime_no(category: int, district: int, station: int, year: int, serial: int) -> str:
    """
    Generate an 18-digit CrimeNo based on its component parameters.
    """
    if not (0 <= category <= 9):
        raise ValueError("Category code must be a single digit (0-9).")
    if not (0 <= district <= 9999):
        raise ValueError("District ID must be a positive integer <= 9999.")
    if not (0 <= station <= 9999):
        raise ValueError("Police Station ID must be a positive integer <= 9999.")
    if not (1900 <= year <= 2099):
        raise ValueError("Year must be between 1900 and 2099.")
    if not (0 <= serial <= 99999):
        raise ValueError("Running serial number must be a positive integer <= 99999.")
        
    return f"{category:1d}{district:04d}{station:04d}{year:04d}{serial:05d}"

def generate_case_no(crime_no: str) -> str:
    """
    Derive the 9-digit CaseNo from a validated CrimeNo.
    """
    if not validate_crime_no(crime_no):
        raise ValueError("Cannot derive CaseNo from an invalid CrimeNo.")
    return crime_no[-9:]

def validate_latitude(lat: float | None) -> bool:
    """
    Validate GPS latitude is within range [-90, 90].
    """
    if lat is None:
        return True
    return -90.0 <= lat <= 90.0

def validate_longitude(lon: float | None) -> bool:
    """
    Validate GPS longitude is within range [-180, 180].
    """
    if lon is None:
        return True
    return -180.0 <= lon <= 180.0

def validate_age(age: int | None) -> bool:
    """
    Validate age is within a realistic human lifespan [0, 125].
    """
    if age is None:
        return True
    return 0 <= age <= 125
