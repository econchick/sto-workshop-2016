#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Lynn Root

import click

import meetup
import utils


#: Global Click defaults
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """PyLadies client for the Meetup API"""
    # Needed to collect the other functions/commands as defined here


@main.command(context_settings=CONTEXT_SETTINGS,
              help="Get data from Meetup")
@click.option("--output", "-o", type=click.Path(),
              help="Output of data files")
@click.option("--config", "-c", type=click.Path(exists=True),
              help="Path to config",
              default="pyladies.ini")
@click.option("--log-level", "-l",
              help="Set logging level.",
              type=click.Choice(['debug', 'info', 'warning', 'error']))
def getdata(output, config, log_level):
    # Parse config
    config = utils.setup_config(config, output)

    # If `loglevel` wasn't a given argument, look at config
    if not log_level:
        log_level = config.get("main", "log_level")
    # If `loglevel` not defined in config, set default
    if not log_level:
        log_level = "debug"

    # Setup logger
    logger = utils.setup_logging(log_level)

    # Let's do this!
    meetup.main(config, logger)


if __name__ == "__main__":
    main()
