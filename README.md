Geo Rester
==========
Just a basic rest server to transform access point MAC sets into a location using Google API

Install
-------

1. To run, install requirements using pip:

```pip install -r requirements.txt```

2. Edit the config file geo.json, and enter your Google API key.

3. Then run application.

```./geo_rest.py```


To test
-------

* create a file with the following details:

```
{
    "apscan_data": [
      {
        "band": "2.4",
        "bssid": "9c:b2:b2:66:c1:be",
        "channel": "5",
        "frequency": 2432,
        "rates": "1.0 - 135.0 Mbps",
        "rssi": -35,
        "security": "wpa-psk",
        "ssid": "HUAWEI-B315-C1BE",
        "timestamp": 1522886457.0,
        "vendor": "HUAWEI TECHNOLOGIES CO.,LTD",
        "width": "20"
      },
      {
        "band": "2.4",
        "bssid": "84:78:ac:b9:76:19",
        "channel": "1",
        "frequency": 2412,
        "rates": "6.5 - 270.0 Mbps",
        "rssi": -56,
        "security": "wpa-eap",
        "ssid": "1 Telkom Connect",
        "timestamp": 1522886457.0,
        "vendor": "Cisco Systems, Inc",
        "width": "20"
      }
}
```

* Then run the following command:
```curl -d @input.json -H "Content-Type: application/json" "http://127.0.0.1:5050/geo"```

* It will return:
```
{
  "error": {
    "code": 404,
    "message": "Not Found",
    "errors": [
      {
        "message": "Not Found",
        "domain": "geolocation",
        "reason": "notFound"
      }
    ]
  }
}
```


* If given a large enough sampleset, it will return:
```
{
  "location": {
    "lat": -XX,
    "lng": YY
  },
  "accuracy": ZZ
}
```
