# -*- coding: utf-8 -*-

from . import sitecfg
from .eve_price_resolver import get_resolver


# Sleepers blue loot
ACD_PRICE = 1500000   # Ancient Coordinates Database
NNA_PRICE = 200000    # Neural Network Analyzer
SDL_PRICE = 500000    # Sleeper Data Library
SDAI_PRICE = 5000000  # Sleeper Drone AI Piece


class GasPrices:
    def __init__(self):
        # IDs
        self.FULLERITE_C50_ID = 30370
        self.FULLERITE_C60_ID = 30371
        self.FULLERITE_C70_ID = 30372
        self.FULLERITE_C72_ID = 30373
        self.FULLERITE_C84_ID = 30374
        self.FULLERITE_C28_ID = 30375
        self.FULLERITE_C32_ID = 30376
        self.FULLERITE_C320_ID = 30377
        self.FULLERITE_C540_ID = 30378
        # prices
        self.FULLERITE_C50_PRICE = 0
        self.FULLERITE_C60_PRICE = 0
        self.FULLERITE_C70_PRICE = 0
        self.FULLERITE_C72_PRICE = 0
        self.FULLERITE_C84_PRICE = 0
        self.FULLERITE_C28_PRICE = 0
        self.FULLERITE_C32_PRICE = 0
        self.FULLERITE_C320_PRICE = 0
        self.FULLERITE_C540_PRICE = 0

    def load_prices(self, config: sitecfg.SiteConfig):
        eveprice = get_resolver(config)
        self.FULLERITE_C28_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C28_ID)
        self.FULLERITE_C32_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C32_ID)
        self.FULLERITE_C50_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C50_ID)
        self.FULLERITE_C60_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C60_ID)
        self.FULLERITE_C70_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C70_ID)
        self.FULLERITE_C72_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C72_ID)
        self.FULLERITE_C84_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C84_ID)
        self.FULLERITE_C320_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C320_ID)
        self.FULLERITE_C540_PRICE = eveprice.Jita_sell_min(self.FULLERITE_C540_ID)
