import urllib
import pytz

from datetime import datetime
from utils import http, dict
mapsbaseurl = "https://maps.googleapis.com/maps/api/{ep}/json?{path}{dest}&key={key}"


async def getlocation(location, key):
    geojs = await http.get(mapsbaseurl.format(ep="geocode", path="address=",
                                              dest=urllib.parse.quote(location),
                                              key=key), res_method="json")

    if geojs is None or len(geojs["results"]) == 0:
        raise Exception("The API returned nothing")

    geo = geojs["results"][0]["geometry"]["location"]
    geoloc = geojs["results"][0]["formatted_address"]

    # Just TRY till you get it
    shortfind = geojs["results"][0]["address_components"]
    for g in shortfind:
        if len(g["short_name"]) == 2:
            country_code = g["short_name"]

    return dict.JsonDict({
        "lat": geo['lat'],
        "lng": geo['lng'],
        "country_code": country_code,
        "location": geoloc
    })


async def currenttime(location, key):
    cords = await getlocation(location, key)
    locjs = await http.get(mapsbaseurl.format(ep="timezone", path="location=",
                                              dest=f"{cords.lat},{cords.lng}&timestamp=865871421&sensor=false",
                                              key=key), res_method="json", no_cache=True)
    if locjs is None:
        raise Exception("The API didn't return any information")

    utctime = datetime.utcnow().replace(tzinfo=pytz.utc)
    newtime = utctime.astimezone(pytz.timezone(locjs["timeZoneId"]))

    return dict.JsonDict({
        "time": newtime,
        "country_code": cords.country_code,
        "timetext": newtime.strftime('%A, %d %B %Y %H:%M'),
        "location": cords.location,
        "timezone": locjs['timeZoneName']
    })
