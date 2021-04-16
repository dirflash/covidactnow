#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/python3
# File name: covidactnow.py
# Date created: 3/31/2021
# Date last modified: 4/1/2021
# Python Version: 3.8.8
# Description: Gather COVID-19 stats and post them to Twitter

import requests
import json
import time
from twython import Twython, TwythonError
import logging
import sys
import os
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()


mystate = "CO"  # Set your state abbreviation here. Must be capitalized.
hashtags = f"#Python"  # Hashtags to be appended to the tweet

### Set up logging parameters ###
logfile = "covidactnow.log"
logging.basicConfig(filename=logfile, level=logging.INFO)

### covidactnow API Key
CAN_KEY = os.environ.get("CAN_API_KEY")

### Twitter authentication stuff ###
APP_KEY = os.environ.get("TWITTER_API_KEY")
APP_SECRET = os.environ.get("TWITTER_API_SECRET")
OAUTH_TOKEN = os.environ.get("TWITTER_OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = os.environ.get("TWITTER_OAUTH_SECRET")
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


def get_time():  # Create a time stamp for log entries
    now = str(time.strftime("%Y/%m/%d %H:%M:%S"))
    return now


def get_data():  # Gather the data
    stateurl = (
        f"https://api.covidactnow.org/v2/state/" + mystate + ".json?apiKey=" + CAN_KEY
    )  # URL for grabbing state data
    streq = requests.get(stateurl).content.decode("utf-8")
    stdata = json.loads(streq)  # convert from json to dict

    if stdata["state"] == mystate:
        ### Format state data ###
        stpop = "{:,}".format(stdata["population"])
        stcases = "{:,}".format(
            stdata["actuals"]["cases"]
        )  # Add commas to number strings
        sttodaycases = "{:,}".format(stdata["actuals"]["newCases"])
        sthospitalizations = "{:,}".format(
            stdata["actuals"]["hospitalBeds"]["currentUsageCovid"]
        )
        stdeaths = "{:,}".format(stdata["actuals"]["deaths"])
        sttodaydeaths = "{:,}".format(stdata["actuals"]["newDeaths"])
        stposrate = "{:.2%}".format(stdata["metrics"]["testPositivityRatio"])
        stfirstdose = "{:,}".format(stdata["actuals"]["vaccinationsInitiated"])
        st1vax = (stdata["actuals"]["vaccinationsInitiated"]) / (stdata["population"])
        st1vaxed = "{:.2%}".format(st1vax)
        stfinaldose = "{:,}".format(stdata["actuals"]["vaccinationsCompleted"])
        stvax = (stdata["actuals"]["vaccinationsCompleted"]) / (stdata["population"])
        stvaxed = "{:.2%}".format(stvax)
        stlastupdated = stdata["lastUpdatedDate"]

        logging.info(f"{get_time()} - Gathered {mystate} data.")
        console.log(f"Gathered {mystate} data.", style="magenta")

    message = (
        f"\nLast 24-hour #COVID-19 data from #Colorado:\n"
        f"{sttodaycases} new cases\n"
        f"{sthospitalizations} hospitalizations\n"
        f"{sttodaydeaths} deaths\n"
        f"{stcases} total cases\n"
        f"{stdeaths} total deaths\n"
        f"{stposrate} state positivity rate\n"
        f"{stfirstdose} ({st1vaxed}) first doses\n"
        f"{stfinaldose} ({stvaxed}) fully vaccinated\n\n"
        f"Stats last updated: {stlastupdated}\n"
    )

    table = Table(title="COVID-19 Statistics for " + mystate, style="green")

    table.add_column("Type", style="green")
    table.add_column("Date", style="green")

    table.add_row("New Cases", sttodaycases)
    table.add_row("Hospitalizations", sthospitalizations)
    table.add_row("Total Cases", stcases)
    table.add_row("Deaths", sttodaydeaths)
    table.add_row("Positivity Rate", stposrate)
    table.add_row("First Dose", stfirstdose)
    table.add_row("First Dose %", st1vaxed)
    table.add_row("Second Dose", stfinaldose)
    table.add_row("Second Dose %", stvaxed)
    table.add_row("Updated", stlastupdated)

    if table.columns:
        console.print(table)
    else:
        print("[i]No data...[/i]")

    logging.info(f"{get_time()} - Tweet created.")
    console.log(f"Tweet created.", style="magenta")

    return message


def main():  # Send Tweet
    xmessage = get_data()
    tmessage = f"{xmessage}\n{hashtags}"
    ### Tweet Message ###
    if len(tmessage) > 280:
        logging.info(
            f"{get_time()} - Message exceeds 280 characters. {len(tmessage)} Tweet not sent."
        )
        console.log(
            f"Message exceeds 280 characters. {len(tmessage)} Tweet not sent.",
            style="bold and red",
        )
        xmessage = f"Message exceeds 280 characters.\n{len(tmessage)}\n Tweet not sent."
        sys.exit()
    else:
        twitter.update_status(status=tmessage)  # Tweet the message
        logging.info(f" Twitter message:\n {tmessage}")
        logging.info(f"{get_time()} - Posted to Twitter.\n")
        console.log(f"Posted to Tweeter.", style="magenta")
        sys.exit()


try:
    main()
except TwythonError as e:
    get_time()
    logging.info(f"{get_time()} - {e}")
