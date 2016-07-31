#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Lynn Root

import requests
import yaml

PYLADIES_YAML = "https://raw.githubusercontent.com/pyladies/pyladies/master/www/config.yml"  # NOQA


def _get_pyladies_yaml():
    # TODO: wrap in try/except
    resp = requests.get(PYLADIES_YAML)
    if resp.ok:
        return resp.text


def get_pyladies_meetup_data():
    data = _get_pyladies_yaml()
    data = yaml.load(data)
    locations = data.get("chapters")

    meetup_info = []
    no_meetup = []
    for location in locations:
        name = location.get("name")
        meetup_id = location.get("meetup_id")
        meetup_name = location.get("meetup")
        if meetup_name:
            meetup_name = meetup_name.split()
            meetup_name = "".join(meetup_name)
        if not meetup_id and not meetup_name:
            no_meetup.append(name)
        else:
            meetup_info.append((name, meetup_id, meetup_name))
    return meetup_info, no_meetup
