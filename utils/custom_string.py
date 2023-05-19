from persiantools import characters
from persiantools.jdatetime import JalaliDate


def replace_arabic(string: str):
    return characters.ar_to_fa(string).strip(" \u200c")


def replace_persian(string: str):
    return characters.fa_to_ar(string).strip(" \u200c")


def convert_to_number_if_number(string: str):
    try:
        return float(string.replace(",", ""))
    except ValueError:
        return string


def convert_jalali_to_gregorian(jalaali_date):
    if not isinstance(jalaali_date, JalaliDate):
        jalaali_date = convert_to_jalali_date(jalaali_date)
    return jalaali_date.to_gregorian()


def convert_to_jalali_date(date):
    delimiter = ""
    if "/" in str(date):
        delimiter = "/"
    elif "-" in str(date):
        delimiter = "-"
    year, month, day = date.split(delimiter)
    return JalaliDate(int(year), int(month), int(day))
