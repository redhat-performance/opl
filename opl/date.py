import logging
import datetime


def my_fromisoformat(string):
    """
    My limited version of datetime.datetime.fromisoformat() function. Only
    accepts one format, only in UTC. Once we are able to run on newer python,
    replace this with said function.
    """
    if string[-1] == "Z":
        string = string[:-1] + "+00:00"
    if string[-6] != "+" and string[-5] != "+":
        logging.warning(f"Date {string} do not have TZ info, assuming '+00:00'")
        string += "+00:00"
    if string[-3] != ":":
        string = string[:-2] + ":" + string[-2:]
    if string.endswith("+00:00"):
        string_tz = datetime.timezone.utc
    elif string.endswith("+01:00"):
        string_tz = datetime.timezone(datetime.timedelta(hours=1))
    elif string.endswith("+02:00"):
        string_tz = datetime.timezone(datetime.timedelta(hours=2))
    else:
        raise ValueError(f"I do not know how to handle timezone of {string}")
    string = string[:-6]
    try:
        out = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        out = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
    out = out.replace(tzinfo=string_tz)
    return out


def get_now_str():
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=datetime.timezone.utc)
    return now.isoformat()
