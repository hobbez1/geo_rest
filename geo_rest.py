#!/usr/bin/env python3
import os
from json import dumps, load
import requests
from bottle import post, run, request

config = {}

def config_reader():
    """Read the config file"""
    if os.path.isfile('geo.json'):
        configs = load(open('geo.json'))
    global config

    config["KEY"] = configs['key']


def load_data():
    """Load existing data if it exists"""
    if os.path.isfile('data.json'):
        data = load(open('data.json'))
        ret_val = (data['macs'], data['groups'])
    else:
        ret_val = ({}, [])
    return ret_val


def save_data():
    """On exit, store cache to a file"""
    with open('data.json', 'w') as fhl:
        fhl.write(dumps({"macs": FOUND_MACS, "groups": FOUND_GROUPS}))


def add_aps(aps, location):
    """If a new location was found, add it to the cache"""
    print("adding to cache")
    print(FOUND_MACS)
    FOUND_GROUPS.append({"aps": aps, "loc": location})
    gid = len(FOUND_GROUPS)-1
    for ap in aps:
        updater = FOUND_MACS.get(ap, [])
        updater.append(gid)
        FOUND_MACS[ap] = updater


def find_blocks(aps):
    """Get a list of all possible similair locations"""
    found = []
    for ap in aps:
        found += FOUND_MACS.get(ap, [])
    # trim down to list to unique set
    found = list(set(found))
    return found

def compare(aps, to_check):
    """Compare ap list to existing lists, returning true if more thank 90% similair"""
    common = [ap for ap in aps if ap in to_check]
    return len(common)/len(aps) > 0.9

def check_cache(aps):
    """Check in cache if this query was done before"""
    to_comp = find_blocks(aps)
    for num in to_comp:
        if compare(aps, FOUND_GROUPS[num]['aps']):
            print("got from cache")
            return FOUND_GROUPS[num]['loc']
    return False


@post("/geo")
def geo():
    """REST url to check location on Google given a set of access point details"""
    translate = {"bssid":"macAddress", "channel": "channel", "rssi": "signalStrength"}
    global config
    geodata = []
    aps = []
    for ap in request.json.get("apscan_data"):
        ap_data = {}
        for gotten, newname in translate.items():
            ap_data[newname] = ap.get(gotten)
        geodata.append(ap_data)
        aps.append(ap["bssid"])
    to_send = {"considerIp": "false", "wifiAccessPoints": geodata}
    maps_url = "https://www.googleapis.com/geolocation/v1/geolocate?key={}".format(config["KEY"])
    cached = check_cache(aps)
    if cached:
        return cached
    else:
        req = requests.post(maps_url, data = dumps(to_send))
        if req.status_code == 200:
            # only add if we got a location
            add_aps(aps, req.text)
        return req.text

def main():
    """Main program"""
    global config, FOUND_MACS, FOUND_GROUPS
    config_reader()
    FOUND_MACS, FOUND_GROUPS = load_data()
    run(host=config.get('host', '127.0.0.1'), port=config.get('port', 5050))
    save_data()


if __name__ == "__main__":
    main()
