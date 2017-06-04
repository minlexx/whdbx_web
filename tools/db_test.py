# -*- coding: utf-8 -*-
from classes import sitecfg
from classes import sitedb


c = sitecfg.SiteCfg()
db = sitedb.SiteDb(c)

# ret = db.find_route(30003067, 30002187)  # Amarr
# ret = db.find_route(30003067, 30000142, 0.5, 25)  # Jita
# ret = db.find_route(30003067, 30002659, 0.5, 25)  # Dodixie
# ret = db.find_route(30003067, 30002053, 0.5, 25)  # Hek
ret = db.find_routes_cache(30003067, 30002510, 0.5, 25, './db/routes_cache')  # Rens

if ret:
    print(db._str_route(ret))
