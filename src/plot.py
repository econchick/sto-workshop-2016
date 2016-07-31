#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Lynn Root

from collections import defaultdict
import datetime
import json
import os

import matplotlib.pyplot as plt


REPO = os.path.abspath(os.path.pardir)
DATA_DIR = os.path.join(REPO, "data")
GROUP_JSON = "pyladies_group.json"
MEMBERS_JSON = "pyladies_members.json"
PUG_MEMBERS_JSON = "{user_group}.json"
IGNORE_JSON = [GROUP_JSON, MEMBERS_JSON]
GROUP_DIRS = [d for d in os.listdir(DATA_DIR)]
PYLADIES_GROUPS = []
for group in GROUP_DIRS:
    if os.path.isdir(os.path.join(DATA_DIR, group)):
        PYLADIES_GROUPS.append(group)


# load group data for a PyLadies Meetup Group
def load_group_data(pyladies_group):
    pyladies_dir = os.path.join(DATA_DIR, pyladies_group)

    # don't load files to ignore
    groups = os.listdir(pyladies_dir)
    for group in IGNORE_JSON:
        try:
            group_index = groups.index(group)
            groups.pop(group_index)
        except ValueError:
            pass
    group_data = []
    for group in groups:
        group_file = os.path.join(pyladies_dir, group)
        with open(group_file, "r") as f:
            data = json.load(f)
        group_name = group.split(".")[:-1]
        group_name = "".join(group_name)
        tmp = dict(name=group_name, data=data)
        group_data.append(tmp)
    return group_data


def pyladies_created(pyladies_group):
    pyladies_dir = os.path.join(DATA_DIR, pyladies_group)
    pyladies_file = os.path.join(pyladies_dir, "pyladies_group.json")
    with open(pyladies_file, "r") as f:
        data = json.load(f)
    created_ms = data.get("created")
    created_s = created_ms / 1000
    created = datetime.datetime.fromtimestamp(created_s)
    year = created.strftime("%Y")
    month = created.strftime("%m")
    day = created.strftime("%d")
    return year, month, day


def get_member_joined(group_member_data):
    joined = [g.get("joined") for g in group_member_data]
    ret = []
    for j in joined:
        if j:  # May be 'None':
            ms = int(j) / 1000
            dt = datetime.datetime.fromtimestamp(ms)
            ret.append(dt)
    return ret


def create_buckets(joined_data):
    buckets = defaultdict(int)
    for member in joined_data:
        # get month & year
        year = member.strftime("%Y")
        month = member.strftime("%m")
        key = "{0}-{1}".format(year, month)
        buckets[key] += 1
    return buckets


def get_member_joined_groups(groups):
    ret = []
    for group in groups:
        joined = get_member_joined(group.get("data"))
        buckets = create_buckets(joined)
        tmp = dict(name=group.get("name"), data=buckets)
        ret.append(tmp)
    return ret


def generate_plot(data):
    legend = []

    for group in data:
        name = group.get("name")
        legend.append(name)
        data = group.get("data")
        plt.plot(data.keys(), data.values())

    plt.legend(legend)

    plt.savefig("example.png")


def main():
    group_data = load_group_data("NYCPyLadies")
    joined_data = get_member_joined_groups(group_data)
    generate_plot(joined_data)


if __name__ == "__main__":
    main()
