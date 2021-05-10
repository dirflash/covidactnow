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

    usurl = f"https://api.covidactnow.org/v2/country/US" + ".json?apiKey=" + CAN_KEY
    usreq = requests.get(usurl).content.decode("utf-8")
    usdata = json.loads(usreq)

    if stdata["state"] == mystate:
        ### Format state data ###
        # stpop = "{:,}".format(stdata["population"])
        stcases = "{:,}".format(
            stdata["actuals"]["cases"]
        )  # Add commas to number strings
        sttodaycases = "{:,}".format(stdata["actuals"]["newCases"])
        sthospitalizations = "{:,}".format(
            stdata["actuals"]["hospitalBeds"]["currentUsageCovid"]
        )
        stdeaths = "{:,}".format(stdata["actuals"]["deaths"])
        sttodaydeaths = "{:,}".format(stdata["actuals"]["newDeaths"])
        posfl = stdata["metrics"]["testPositivityRatio"]
        stposrate = "{:.2%}".format(posfl)
        stfirstdose = "{:,}".format(stdata["actuals"]["vaccinationsInitiated"])
        st1vax = (stdata["actuals"]["vaccinationsInitiated"]) / (stdata["population"])
        st1vaxed = "{:.2%}".format(st1vax)
        stfinaldose = "{:,}".format(stdata["actuals"]["vaccinationsCompleted"])
        stvax = (stdata["actuals"]["vaccinationsCompleted"]) / (stdata["population"])
        stvaxed = "{:.2%}".format(stvax)
        stlastupdated = stdata["lastUpdatedDate"]

        logging.info(f"{get_time()} - Gathered {mystate} data.")
        console.log(f"Gathered {mystate} data.", style="magenta")

        pos = int(posfl * 1000)
        if pos <= 50:
            posmo = ":smiley:"
        else:
            posmo = ""

        uscases = "{:,}".format(usdata["actuals"]["cases"])
        ustodaycases = "{:,}".format(usdata["actuals"]["newCases"])
        usdeaths = "{:,}".format(usdata["actuals"]["deaths"])
        ustodaydeaths = "{:,}".format(usdata["actuals"]["newDeaths"])

    message = (
        f"\nLast 24-hour #COVID-19 data from #Colorado:\n"
        f"{sttodaycases} new cases\n"
        f"{sthospitalizations} hospitalizations\n"
        f"{sttodaydeaths} deaths\n"
        f"{stcases} total cases\n"
        f"{stdeaths} total deaths\n"
        f"{stposrate} state positivity rate\n"
        f"{stfirstdose} ({st1vaxed}) first doses\n"
        f"{stfinaldose} ({stvaxed}) fully vaxed\n\n"
        f"{usdeaths} US deaths\n\n"
        f"Stats updated: {stlastupdated}\n"
    )

    sttable = Table(title="COVID-19 Statistics for " + mystate, style="green")

    sttable.add_column("Type", style="green")
    sttable.add_column("Data", justify="right", style="green")

    sttable.add_row("New Cases", sttodaycases)
    sttable.add_row("Hospitalizations", sthospitalizations)
    sttable.add_row("Total Cases", stcases)
    sttable.add_row("Deaths", sttodaydeaths)
    sttable.add_row("Positivity Rate", stposrate)
    sttable.add_row("Emoji", posmo)
    sttable.add_row("First Dose", stfirstdose)
    sttable.add_row("First Dose %", st1vaxed)
    sttable.add_row("Second Dose", stfinaldose)
    sttable.add_row("Second Dose %", stvaxed)
    sttable.add_row("Updated", stlastupdated)

    if sttable.columns:
        console.print(sttable)
    else:
        print("[i]No data...[/i]")

    ustable = Table(title="COVID-19 Statistics for US", style="green")

    ustable.add_column("Type", style="green")
    ustable.add_column("Data", justify="right", style="green")

    ustable.add_row("New Cases", ustodaycases)
    ustable.add_row("Total Cases", uscases)
    ustable.add_row("Deaths", ustodaydeaths)
    ustable.add_row("Total Deaths", usdeaths)

    if ustable.columns:
        console.print(ustable)
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
            style="bold red",
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
