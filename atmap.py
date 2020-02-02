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
    for weatheri in weather:
        dgr = 0
        sh = 0
        (inteni, desci, preci, obsci, otheri) = weatheri
        if otheri in ["FC", "DS", "SS"] or obsci in ["VA", "SA"] or preci in ["GR", "PL"]:
            dgr = 24

        if desci == "TS":
            dgr = 30 if inteni == "+" else 24

        if preci == "GS":
            dgr = 18

        if phenomena is None or dgr > phenomena:
            phenomena = dgr

        if desci == "SH":
            sh = 1 if inteni == "-" else 2

        if showers is None or showers < sh:
            showers = sh

    return (phenomena, showers)


def __dangerous_clouds(sky: []):
    cb = 0
    tcu = 0
    for skyi in sky:
        cbi = 0
        tcui = 0
        (cover, height, cloud) = skyi

        if cover == "OVC":
            if cloud == "TCU":
                tcui = 10

            if cloud == "CB":
                cbi = 12

        if cover == "BKN":
            if cloud == "TCU":
                tcui = 8

            if cloud == "CB":
                cbi = 10

        if cover == "SCT":
            if cloud == "TCU":
                tcui = 5

            if cloud == "CB":
                cbi = 6

        if cover == "FEW":
            if cloud == "TCU":
                tcui = 3

            if cloud == "CB":
                cbi = 4

        if cbi > cb:
            cb = cbi

        if tcui > tcu:
            tcu = tcui

    return (cb, tcu, None)


def _get_wind_coef(metar: Metar.Metar):
    spd = metar.wind_speed.value()
    gust = metar.wind_gust.value() if metar.wind_gust is not None else None
    coef = 0

    if 16 <= spd <= 20:
        coef = 1

    if 21 <= spd <= 30:
        coef = 2

    if spd > 30:
        coef = 4

    if gust is not None:
        coef += 1

    return coef


def _get_precipitation_coef(metar: Metar.Metar):
    coef = 0
    for weatheri in metar.weather:
        coefi = 0
        (inteni, desci, preci, obsci, otheri) = weatheri
        if desci == "FZ":
            coefi = 3

        if preci == "SN":
            coefi = 2 if inteni == "-" else 3

        if preci == "SG" or (preci == "RA" and inteni == "+"):
            coefi = 2

        if preci in ["RA", "UP", "IC", "DZ"]:
            coefi = 1

        if coefi > coef:
            coef = coefi

    return coef


def _get_freezing_coef(metar: Metar.Metar):
    tt = metar.temp.value()
    dp = metar.dewpt.value()
    diff = tt - dp
    moisture = None
    for weatheri in metar.weather:
        moist = 0
        (inteni, desci, preci, obsci, otheri) = weatheri
        if desci == "FZ":
            moist = 5

        if preci == "SN":
            moist = 4 if inteni == "-" else 5

        if preci in ["SG", "RASN"] or (preci == "RA" and inteni == "+") or obsci == "BR":
            moist = 4

        if preci in ["DZ", "IC", "RA", "UP", "GR", "GS", "PL"] or obsci == "FG":
            moist = 3

        if moisture is None or moisture < moist:
            moisture = moist

    if tt <= 3 and moisture == 5:
        return 4

    if tt <= -15 and moisture is not None:
        return 4

    if tt <= 3 and moisture == 4:
        return 3

    if tt <= 3 and (moisture == 3 or diff < 3):
        return 1

    if tt <= 3 and moisture is None:
        return 0

    if tt > 3 and moisture is not None:
        return 0

    if tt > 3 and (moisture is None or diff >= 3):
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
    for skyi in metar.sky:
        (cover, height, cloud) = skyi
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
