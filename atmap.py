from metar import Metar


def bad_weather_classes(obs: str):
    metar = Metar.Metar(obs, strict=False)
    ceiling = _get_visibility_ceiling_coef(metar)
    wind = _get_wind_coef(metar)
    precip = _get_precipitation_coef(metar)
    freezing = _get_freezing_coef(metar)
    phenomena = _get_dangerous_phenomena_coef(metar)

    return (ceiling, wind, precip, freezing, phenomena)


def _get_dangerous_phenomena_coef(metar: Metar.Metar):
    phenomena, showers = __dangerous_weather(metar.weather)
    cb, tcu, ts = __dangerous_clouds(metar.sky)
    if showers is not None and showers > 0:
        if cb == 12:
            ts = 18 if showers == 1 else 24

        if cb == 10 or tcu == 10:
            ts = 12 if showers == 1 else 20

        if cb == 6 or tcu == 8:
            ts = 10 if showers == 1 else 15

        if cb == 4 or tcu == 5:
            ts = 8 if showers == 1 else 12

        if tcu == 3:
            ts = 4 if showers == 1 else 6

    return max(i for i in [phenomena, cb, tcu, ts] if i is not None)


def __dangerous_weather(weather: []):
    phenomena = None
    showers = None
    for intensity, desc, precip, obs, other in weather:
        __phenomena = 0
        __showers = 0
        if other in ["FC", "DS", "SS"] or obs in ["VA", "SA"] or precip in ["GR", "PL"]:
            __phenomena = 24

        if desc == "TS":
            __phenomena = 30 if intensity == "+" else 24

        if precip == "GS":
            __phenomena = 18

        if phenomena is None or __phenomena > phenomena:
            phenomena = __phenomena

        if desc == "SH":
            __showers = 1 if intensity == "-" else 2

        if showers is None or __showers > showers:
            showers = __showers

    return (phenomena, showers)


def __dangerous_clouds(sky: []):
    cb = 0
    tcu = 0
    for cover, height, cloud in sky:
        __cb = 0
        __tcu = 0
        if cover == "OVC":
            if cloud == "TCU":
                __tcu = 10

            if cloud == "CB":
                __cb = 12

        if cover == "BKN":
            if cloud == "TCU":
                __tcu = 8

            if cloud == "CB":
                __cb = 10

        if cover == "SCT":
            if cloud == "TCU":
                __tcu = 5

            if cloud == "CB":
                __cb = 6

        if cover == "FEW":
            if cloud == "TCU":
                __tcu = 3

            if cloud == "CB":
                __cb = 4

        if __cb > cb:
            cb = __cb

        if __tcu > tcu:
            tcu = __tcu

    return (cb, tcu, None)


def _get_wind_coef(metar: Metar.Metar):
    spd = metar.wind_speed.value()
    gusts = metar.wind_gust.value() if metar.wind_gust is not None else None
    coef = 0

    if 16 <= spd <= 20:
        coef = 1

    if 21 <= spd <= 30:
        coef = 2

    if spd > 30:
        coef = 4

    if gusts is not None:
        coef += 1

    return coef


def _get_precipitation_coef(metar: Metar.Metar):
    coef = 0
    for intensity, desc, precip, obs, other in metar.weather:
        __coef = 0
        if desc == "FZ":
            __coef = 3

        if precip == "SN":
            __coef = 2 if intensity == "-" else 3

        if precip == "SG" or (precip == "RA" and intensity == "+"):
            __coef = 2

        if precip in ["RA", "UP", "IC", "DZ"]:
            __coef = 1

        if __coef > coef:
            coef = __coef

    return coef


def _get_freezing_coef(metar: Metar.Metar):
    tt = metar.temp.value()
    dp = metar.dewpt.value()
    moisture = None
    for intensity, desc, precip, obs, other in metar.weather:
        __moisture = 0
        if desc == "FZ":
            __moisture = 5

        if precip == "SN":
            __moisture = 4 if inteni == "-" else 5

        if precip in ["SG", "RASN"] or (precip == "RA" and intensity == "+") or obs == "BR":
            __moisture = 4

        if precip in ["DZ", "IC", "RA", "UP", "GR", "GS", "PL"] or obs == "FG":
            __moisture = 3

        if moisture is None or __moisture > moisture:
            moisture = __moisture

    if tt <= 3 and moisture == 5:
        return 4

    if tt <= -15 and moisture is not None:
        return 4

    if tt <= 3 and moisture == 4:
        return 3

    if tt <= 3 and (moisture == 3 or (tt - dp) < 3):
        return 1

    if tt <= 3 and moisture is None:
        return 0

    if tt > 3 and moisture is not None:
        return 0

    if tt > 3 and (moisture is None or (tt - dp) >= 3):
        return 0

    return 0


def _get_visibility_ceiling_coef(metar: Metar.Metar):
    vis = __get_visibility(metar)
    is_covered, cld_base = __get_ceiling(metar)

    if (vis <= 325) or (is_covered and cld_base <= 50):
        return 5

    if (350 <= vis <= 500) or (is_covered and 100 <= cld_base <= 150):
        return 4

    if (550 <= vis <= 750) or (is_covered and 200 <= cld_base <= 250):
        return 2

    return 0


def __get_ceiling(metar: Metar.Metar):
    cld_cover = False
    cld_base = None
    for cover, height, cloud in metar.sky:
        if cover in ["BKN", "OVC"]:
            cld_cover = True

        if height is not None and (cld_base is None or cld_base > height.value()):
            cld_base = height.value()

    return (cld_cover, cld_base)


def __get_visibility(metar: Metar.Metar):
    vis = metar.vis.value()
    rvr = None
    for name, low, high, unit in metar.runway:
        if rvr is None or rvr > low.value():
            rvr = low.value()

    if rvr is not None and rvr < 1500:
        vis = rvr

    return vis
