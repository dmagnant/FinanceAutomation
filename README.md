# Finance Automation Project

## PROBLEM:

As an individual investor I would like to track my personal finances, but I do not want to provide my credentials to a 3rd party aggregator like Mint.

## SOLUTION:

I created an application that allows for creation of scripts to login and export transactions from banking websites and import into GnuCash. Further, there are scripts that allow for automatic redemption of rewards points for applicable accounts.

## PREREQUISITES:

-GnuCash (open-source accounting software)
-Keepass (password management)
-Selenium-compatible browser installed
-Python

## TO RUN:

running the Launch.py file will start the Django application locally as well as launch Chrome in remote debugging mode
From there, user can navigate to respective script page and launch desired scripts

## NOTABLE FEATURES:

NOTABLE FEATURES:

-Selenium-based scripts
-Django front-end to run scripts/view websites
-Password management through keepass