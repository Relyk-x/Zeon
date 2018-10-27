import json
import urllib

from utils import http, dict


async def getcords(address, key):
    try:
        r = await http.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={key}",
            res_method="json"
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError("The API didn't give any response")

    results = r["results"][0]

    geometry = results["geometry"]["viewport"]["northeast"]
    address = results["formatted_address"]

    # Just TRY till you get it
    shortfind = results["address_components"]
    for g in shortfind:
        if len(g["short_name"]) == 2:
            country_code = g["short_name"]

    return dict.JsonDict({
        "country_code": country_code,
        "address": address,
        "geometry": geometry,
        "latitude": geometry["lat"],
        "longitude": geometry["lng"]
    })


async def getweather(address, key, gmapskey, unit="ca"):
    cords = await getcords(address, gmapskey)
    lat = cords.latitude
    lng = cords.longitude

    try:
        r = await http.get(
            f"https://api.darksky.net/forecast/{key}/{lat},{lng}?units={unit}",
            res_method="json"
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError("The API didn't give any response")

    return dict.JsonDict({
        "country_code": cords.country_code,
        "address": cords.address,
        "currently": dict.JsonDict(r["currently"]),
        "one": dict.JsonDict(r["daily"]["data"][0]),
        "two": dict.JsonDict(r["daily"]["data"][1]),
        "three": dict.JsonDict(r["daily"]["data"][2]),
        "four": dict.JsonDict(r["daily"]["data"][3]),
        "five": dict.JsonDict(r["daily"]["data"][4]),
    })
