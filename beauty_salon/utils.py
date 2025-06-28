import calendar

from django.utils import timezone
from phonenumbers import NumberParseException, is_valid_number, parse


def validate_phone(phone):
    try:
        phone_obj = parse(phone, "RU")
        return is_valid_number(phone_obj)
    except NumberParseException:
        return False 


def get_ru_month(month):
    months_ru = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    return months_ru[month]


def get_month_info():
    now = timezone.now()
    current_year = now.year
    current_month_num = now.month
    current_month_name = get_ru_month(current_month_num)
    first_day_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if current_month_num == 12:
        first_day_next_month = first_day_current_month.replace(year=current_year + 1, month=1)
    else:
        first_day_next_month = first_day_current_month.replace(month=current_month_num + 1)
    return {
        "year": current_year,
        "month_num": current_month_num,
        "month_name": current_month_name,
        "first_day": first_day_current_month,
        "first_day_next": first_day_next_month,
    }