#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Lynn Root

import logging
import os
import time

import requests

from src.github import get_pyladies_meetup_data
from src.utils import save_output, setup_config


logger = logging.getLogger("pyladies.meetup")


class MeetupApi(object):
    """
    Simple class to handle calls to the Meetup API
    """
    logger = logging.getLogger("pyladies.meetup.api")

    def __init__(self, config):
        self.meetup_host = config.get("meetup", "host")
        self.params = {
            "signed": True,
            "key": config.get("meetup", "api_key")
        }

    # TODO: add try/except
    def get_request(self, endpoint, addl_params={}):
        for k, v in addl_params.items():
            self.params[k] = v

        url = self.meetup_host + endpoint
        while url is not None:
            data = {}
            time.sleep(1)
            resp = requests.get(url, self.params)
            logger.debug("REQ URL: {0}".format(resp.request.url))
            if resp.ok:
                data = resp.json()
                if "results" not in data:
                    return
                yield data.get("results")
            url = data.get("meta", {}).get("next")
            if url is "":
                url = None


class MeetupGroups(object):
    """
    Class to call & parse data from the Meetup Groups API endpoint.
    """
    logger = logging.getLogger("pyladies.meetup.groups")

    def __init__(self, config):
        self.config = config
        self.endpoint = "/groups"
        self.api = MeetupApi(config)

    def _get_pyladies(self, meetup_names):
        meetup_group_data = []
        for name, gid, url_name in meetup_names:
            addl_params = {"group_id": gid, "group_urlname": url_name}
            time.sleep(.5)
            req = self.api.get_request(self.endpoint, addl_params)

            for r in req:
                # naive error check, should only return one
                if not r or len(r) < 1:
                    err = "Error finding group info for {0}".format(name)
                    logger.error(err)
                    continue
                elif len(r) > 1:
                    err = "Received more than one PyLadies for {0}".format(
                        name
                    )
                    logger.error(err)
                    continue
                else:
                    logger.debug("Found Meetup data for {0}".format(name))
                    meetup_group_data.append(r[0])
        return meetup_group_data

    def get_pyladies(self):
        meetup_info, no_meetup = get_pyladies_meetup_data()
        meetup_group_data = self._get_pyladies(meetup_info)

        count = len(meetup_group_data)
        logger.debug("Found {0} PyLadies groups".format(count))
        msg = "{0} PyLadies do not have Meetup data".format(len(no_meetup))
        logger.debug(msg)
        return meetup_group_data


class PythonUserGroup(object):
    logger = logging.getLogger("pyladies.meetup.members")

    def __init__(self, group_data, config):
        self.data        = group_data
        self.name        = group_data.get("name")
        self.config      = config
        self.endpoint    = "/members"
        self.api         = MeetupApi(config)
        self.json_output = self._clean_name() + ".json"

    def _clean_name(self):
        blacklist_filechars = ",:;/\\*[](){}"
        for char in blacklist_filechars:
            if char in self.name:
                self.name = self.name.replace(char, "")
        name = self.name.split()
        return "".join(name)

    def get_members(self):
        member_count = self.data.get("members")
        log = "Getting data for {0} members in Meetup group '{1}'".format(
            member_count, self.name
        )
        self.logger.debug(log)

        addl_params = {"group_id": self.data.get("id")}

        members = []
        req = self.api.get_request(self.endpoint, addl_params)
        for r in req:
            members.extend(r)

        self.logger.info("Got {0} members for {1}".format(len(members),
                                                          self.name))
        return members


class PyLadiesGroup(PythonUserGroup):
    def __init__(self, data, config):
        super(PyLadiesGroup, self).__init__(data, config)
        self.pylady_dir     = self._create_pylady_directory()
        self.api = MeetupApi(config)

    def _create_pylady_directory(self):
        # Clean name of directory by removing space chars
        # e.g. PyLadies San Francisco -> PyLadiesSanFrancisco
        pylady_dirname = self._clean_name()

        # Create directory within desired output directory
        # e.g. data/PyLadiesSanFrancisco/
        # TODO: will error out if no `[main]` section
        output_dir = self.config["main"].get("output_dir")
        output_dir = os.path.join(output_dir, pylady_dirname)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir

    def is_pug(self, group):
        """
        Naive func to designate if group name is a Python User Group (pug).
        Return ``True`` if in ``SEARCH`` key words and not in ``OMIT``
        keywords.

        :param dict group: group data
        :ret: If a PUG or not
        :rtype: bool
        """
        blacklist_terms = self.config.get("meetup", "pug_blacklist")
        blacklist_terms = blacklist_terms.split(",")
        blacklist_terms = [t.strip() for t in blacklist_terms]
        whitelist_terms = self.config.get("meetup", "pug_whitelist")
        whitelist_terms = whitelist_terms.split(",")
        whitelist_terms = [t.strip() for t in whitelist_terms]
        group_name = group.get("name").lower()

        for o in blacklist_terms:
            if o in group_name:
                return False
        for s in whitelist_terms:
            if s in group_name:
                return True
        return False

    def get_nearby_pugs(self):
        self.logger.debug("Finding nearby PUGs for {0}".format(self.name))

        addl_params = {
            "lat": self.data.get("lat"),
            "lon": self.data.get("lon"),
            "radius": 50.0,  # miles
            "category_id": 34,
            "page": 200,
        }
        req = self.api.get_request("/groups", addl_params)
        groups = []
        for r in req:
            groups.extend(r)

        nearby = [g for g in groups if self.is_pug(g)]

        log = "Found {0} PUGs within 50 miles of {1}".format(len(nearby),
                                                             self.name)
        self.logger.debug(log)
        return nearby


def get_meetup_data(config):
    # Setup config
    config = setup_config(config)
    main(config)


def main(config, loglevel='debug'):
    # Get meetup group data
    log = "Getting PyLadies Meetup groups data"
    logger.info(log)
    group_obj = MeetupGroups(config)
    pyladies = group_obj.get_pyladies()
    log = "Found {0} PyLadies groups".format(len(pyladies))
    logger.info(log)

    logger.info("Getting member data for nearby PUGs & PyLadies groups")
    for p in pyladies:
        pylady = PyLadiesGroup(p, config)

        # Save PyLadies meetup data
        output = os.path.join(pylady.pylady_dir, "pyladies_group.json")
        save_output(pylady.data, output)

        # Get PyLadies member data...
        pylady_members = pylady.get_members()
        # ..and save the data
        members_output = os.path.join(pylady.pylady_dir,
                                      "pyladies_members.json")
        save_output(pylady_members, members_output)

        # Find nearby PUGs
        nearby_pugs = pylady.get_nearby_pugs()
        # Get nearby PUG member data...
        for p in nearby_pugs:
            pug = PythonUserGroup(p, config)
            pug_members = pug.get_members()
            # ... and save the data
            output_file = os.path.join(pylady.pylady_dir, pug.json_output)
            save_output(pug_members, output_file)
