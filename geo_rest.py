#!/usr/bin/env python3
import os
from json import dumps, load
import requests
from bottle import Bottle, request
import click


class GeoServe:
    """Class for grabbing geo data given wifi details"""
    def __init__(self, conf_file):
        """Setup for class"""
        self.config = {}
        if os.path.isfile(conf_file):
            self.config = load(open(conf_file))

        # load data if already existing
        if os.path.isfile("data.json"):
            data = load(open("data.json"))
            ret_val = (data["macs"], data["groups"])
        else:
            ret_val = ({}, [])
        self.found_macs, self.found_groups =  ret_val

        self._host = self.config.get("host", "127.0.0.1")
        self._port = self.config.get("port", 5050)
        self._app = Bottle()
        self._route()


    def _route(self):
        """Setup routing"""
        self._app.post("/geo", callback=self._geo)


    def start(self):
        """Start wsgi server"""
        self._app.run(host=self._host, port=self._port)


    def save_data(self):
        """On exit, store cache to a file"""
        with open("data.json", "w") as fhl:
            fhl.write(dumps({"macs": self.found_macs, "groups": self.found_groups}))


    def _add_aps(self, aps, location):
        """If a new location was found, add it to the cache"""
        self.found_groups.append({"aps": aps, "loc": location})
        gid = len(self.found_groups)-1
        for local_ap in aps:
            updater = self.found_macs.get(local_ap, [])
            updater.append(gid)
            self.found_macs[local_ap] = updater


    def _find_blocks(self, aps):
        """Get a list of all possible similair locations"""
        found = []
        for local_ap in aps:
            found += self.found_macs.get(local_ap, [])
        # trim down to list to unique set
        found = list(set(found))
        return found


    def _check_cache(self, aps):
        """Check in cache if this query was done before"""
        def compare(aps, to_check):
            """Compare ap list to existing lists, returning true if more thank 90% similair"""
            common = [local_ap for local_ap in aps if local_ap in to_check]
            return len(common)/len(aps) > 0.9
        to_comp = self._find_blocks(aps)
        for num in to_comp:
            if compare(aps, self.found_groups[num]["aps"]):
                return self.found_groups[num]["loc"]
        return False


    def _geo(self):
        """REST url to check location on Google given a set of access point details"""
        translate = {"bssid":"macAddress", "channel": "channel", "rssi": "signalStrength"}
        geodata = []
        aps = []
        for local_ap in request.json.get("apscan_data"):
            ap_data = {}
            for gotten, newname in translate.items():
                ap_data[newname] = local_ap.get(gotten)
            geodata.append(ap_data)
            aps.append(local_ap["bssid"])
        to_send = {"considerIp": "false", "wifiAccessPoints": geodata}
        maps_url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.config['key']}"
        cached = self._check_cache(aps)
        if cached:
            data = cached
        else:
            req = requests.post(maps_url, data = dumps(to_send))
            if req.status_code == 200:
                # only add if we got a location
                self._add_aps(aps, req.text)
            data = req.text
        return data

@click.command()
@click.option('--conf', default="geo.json", help='Config file.')
def server_start(conf):
    """Main program"""
    server = GeoServe(conf)
    server.start()
    server.save_data()


if __name__ == "__main__":
    server_start()
