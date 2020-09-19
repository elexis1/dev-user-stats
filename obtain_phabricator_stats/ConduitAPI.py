#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Soruce: https://github.com/elexis1/limnoria-phabricator:
# Provides some abstraction and parsing of the RESTful Phabricator API
import json
import http.client
import urllib.parse

class ConduitAPI:

    def __init__(self, phabricatorURL, phabricatorToken, acceptInvalidSSLCert, httpTimeout):
        self.phabricatorToken = phabricatorToken
        self.phabricatorURL = phabricatorURL
        self.acceptInvalidSSLCert = acceptInvalidSSLCert
        self.httpTimeout = httpTimeout

    # Send an HTTPS GET request to the phabricator location and
    # return the interpreted JSON object
    def queryAPI(self, path, params):

        if self.phabricatorURL is None or self.phabricatorURL == "":
            print("Error: You must configure the Phabricator location!")
            return None

        if self.phabricatorToken is None or self.phabricatorToken == "":
            print("Error: You must configure a Phabricator API token!")
            return None

        params["api.token"] = self.phabricatorToken

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Charset": "utf-8"
        }

        conn = http.client.HTTPSConnection(
            self.phabricatorURL,
            context=ssl._create_unverified_context() if self.acceptInvalidSSLCert else None,
            timeout=self.httpTimeout)

        try:
            conn.request("GET", path, urllib.parse.urlencode(params, True), headers)
            response = conn.getresponse()
        # This is supposedly TimeoutError, but not when testing
        except socket.timeout:
            print("Timeout at", path)
            return None

        if response.status != 200:
            print(response.status, response.reason)
            conn.close()
            return None

        data = response.read()
        conn.close()
        data = json.loads(data.decode("utf-8"))

        if data["error_code"] is not None:
            print("Error:", data["error_info"])
            print("Query:", path, params)
            return None

        return data.get("result")

    # Return some information about arbitrary objects, like
    # differntials, users, commits, transactions, ...
    def queryPHIDs(self, phids):

        if len(phids) == 0:
            return []

        return self.queryAPI("/api/phid.query", {"phids[]": phids})

    # Fetches some phabricator stories after the given chronological key,
    # Only yields story PHID, author PHIDs and the PHIDs of the associated object
    def queryFeed(self, chronokey, storyLimit, historyForwards):

        arguments = {
            'limit': storyLimit,
            'view': "data"
        }

        # Query stories before or after the given chronokey,
        # otherwise query for the most recent ones (as of now)
        if chronokey is not None:
            if historyForwards:
                arguments["before"] = chronokey
            else:
                arguments["after"] = chronokey

        return self.queryAPI("/api/feed.query", arguments)

