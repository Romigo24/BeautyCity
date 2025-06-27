from phonenumbers import NumberParseException, is_valid_number, parse


def validate_phone(phone):
    try:
        phone_obj = parse(phone, "RU")
        return is_valid_number(phone_obj)
    except NumberParseException:
        return False