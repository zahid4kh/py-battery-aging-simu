def days_to_hours(days: float) -> float:
    return days * 24.0

def hours_to_days(hours: float) -> float:
    return hours / 24.0

def years_to_hours(years: float) -> float:
    hours_in_one_year = 24.0 * 365.0
    return years * hours_in_one_year

def weeks_to_hours(weeks: float) -> float:
    hours_in_one_week = 24.0 * 7.0
    return weeks * hours_in_one_week

def celsius_to_kelvin(celsius: float) -> float:
    return celsius + 273.15

def kelvin_to_celsius(kelvin: float) -> float:
    return kelvin - 273.15