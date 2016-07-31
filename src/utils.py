#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Lynn Root

import configparser
import json
import logging
import os


def get_abs_path(output):
    # if it has a leading "/", assume that it's the
    # absolute path
    if output.startswith("/"):
        return output
    # otherwise, assume relative path to where the
    # script is being ran (aka current working dir)
    cwd = os.getcwd()
    output = os.path.join(cwd, output)
    return os.path.abspath(output)


def setup_config(config_file, output=None):
    """
    Setup configuration for project.

    :param file config_file: ``.ini`` file to be parsed
    :returns: ConfigParser instance
    """
    config = configparser.RawConfigParser()
    config.read(config_file)

    # TODO: will probably error if no `[main]` section
    # if the output is given via CLI, prefer that one
    if output:
        config["main"]["output_dir"] = get_abs_path(output)
    # if not given in CLI, and not set in config, then default
    # to "data" relative to cwd
    elif not config["main"].get("output_dir"):
        config["main"]["output_dir"] = get_abs_path("data")
    # else, it should be set in the config, therefore we should
    # make sure it also has an abspath
    else:
        config_output = config["main"].get("output_dir")
        config_output = get_abs_path(config_output)
        config["main"]["output_dir"] = config_output

    return config


def setup_logging(log_level):
    """Helper func to setup logging.

    :param str log_level: user-specified log level
    :ret: ``logger`` object
    """
    # Create a new `logger` object
    logger = logging.getLogger("pyladies")
    # Set the desired logging level
    level = getattr(logging, log_level.upper())
    logger.setLevel(level)
    # Create console handler (logs to the terminal)
    console_stream = logging.StreamHandler()
    # Format how the log messages are printed. Outputs like:
    # 2016-03-19 15:10:26,618 - pyladies - DEBUG - some debug message
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    # Attach the formatter to console_stream
    console_stream.setFormatter(formatter)
    # Add `console_stream` to `logger` object
    logger.addHandler(console_stream)

    return logger


def save_output(data, output_file):
    with open(output_file, "w") as f:
        json.dump(data, f)
