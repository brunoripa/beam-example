import random
import uuid
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ROWS_NUMBER = 10000
USERS_NUMBER = 200
FILENAME = 'input.txt'
SEPARATOR = ','

# Seconds, will be divided by 10
DURATION = range(1, 50)
COUNTRIES = json.load(open('countries.json', 'rb'))
STR_COUNTRIES = []
USERS = [str(uuid.uuid4()) for x in range(USERS_NUMBER)]
NAMES = []

# Reading the user names
with open("names.txt", "rb") as names_handle:
    NAMES = names_handle.readlines()

NAMES = [x.strip().strip(" ") for x in NAMES]


# Generating country names (some of them contain ',' in the names)
# eg: "Man, Isle of". Rewriting to "Isle of Man"
for x in COUNTRIES:
    name = x['Name']

    if ',' in name:
        country, prefix = name.split(",")
        name = "{} {}".format(prefix.strip(), country.strip())

    try:
        STR_COUNTRIES.append(
            "{} ({})".format(
                name, x['Code']
            )
        )
    except UnicodeEncodeError:
        logger.info('Skipping %s', x['Name'].encode('utf8'))


# Generating output file
with open(FILENAME, 'wb') as handle:
    for entry in range(ROWS_NUMBER):
        handle.write(
            SEPARATOR.join(
                (
                    str(random.choice(STR_COUNTRIES)),
                    str(random.choice(DURATION)/10.0),
                    random.choice(NAMES)
                )
            ) + "\n"
        )
