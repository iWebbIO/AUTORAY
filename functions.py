import datetime
import pytz
import re
import random
import string


def create_file(filename):
    with open(filename, "a") as f:
        f.close()


def generate(length):
    characters = string.ascii_letters + string.digits
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def days(s):
    # define a dictionary of conversion factors
    factors = {"d": 1, "m": 30, "y": 365}
    # find the number and unit in the string
    match = re.search(r"(\d+)(\w)", s)
    if match:
        # get the number and unit from the match object
        num = int(match.group(1))
        unit = match.group(2)
        # multiply the number by the factor corresponding to the unit
        return num * factors[unit]
    else:
        # return None if no match is found
        return None


def get_current_time():
    # Set the time zone to Iran
    iran_tz = pytz.timezone("Asia/Tehran")

    # Get the current time in Iran
    current_time = datetime.now(iran_tz)

    # Format the time as "Day_Of_the_week Hour:Minute"
    formatted_time = current_time.strftime("%A %H:%M")

    return formatted_time