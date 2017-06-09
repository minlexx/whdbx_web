# -*- coding: utf-8 -*-

from . import database
from . import sitecfg
from . import sleeper
from . import loot_prices


class WHSignatureWave:
    def __init__(self, sig_id: int):
        self.sig_id = sig_id
        self.wave_id = 0
        self.is_capital = False
        self.sleepers_str = ''
        self.sleeper_ids = []
        self.sleeper_count = []
        self.sleeper_abilities = []
        self.sleepers = []
        # stats
        self.total_dps = 0
        self.total_isk = 0
        self.total_ehp = 0

    def initfromrow(self, row: tuple):
        #  sig_id, wave_id, is_capital, sleepers
        if row is None:
            pass
        self.wave_id = int(row[1])
        self.is_capital = False
        if int(row[2]) != 0:
            self.is_capital = True
        self.sleepers_str = row[3]

    def load_sleepers(self, db: database.SiteDb):
        #  'sleeper_id:count:abilities,sleeper_id:count:abilities,...'
        if self.sleepers_str == '':
            return
        sl_defs = self.sleepers_str.split(',')
        for sl_def in sl_defs:
            #  'sleeper_id:count:abilities'
            #  or 'sleeper_id:count'
            sl_def = sl_def.strip()
            sl_def_list = sl_def.split(':')
            sl_id = int(sl_def_list[0])
            if sl_id > 0:
                sl_count = int(sl_def_list[1])
                sl_abilities = ''
                if len(sl_def_list) > 2:
                    sl_abilities = sl_def_list[2]
                self.sleeper_ids.append(sl_id)
                self.sleeper_count.append(sl_count)
                self.sleeper_abilities.append(sl_abilities)
        i = 0
        for sl_id in self.sleeper_ids:
            sl = sleeper.WHSleeper()
            sl.load_info(int(sl_id), db)
            sl.set_abilities_from_wave(self.sleeper_abilities[i])
            sl.set_count(self.sleeper_count[i])
            self.sleepers.append(sl)
            i += 1
        # return sl

    def calc_stats(self):
        self.total_dps = 0
        self.total_isk = 0
        self.total_ehp = 0
        i = 0
        for sl in self.sleepers:
            #  sl = sleeper.WHSleeper() # hint
            cnt = self.sleeper_count[i]
            self.total_dps += sl.dps_total * cnt
            self.total_ehp += sl.ehp_total * cnt
            self.total_isk += sl.loot_total * cnt
            i += 1

    def __str__(self):
        s = 'Wave {0}: '.format(self.wave_id)
        if self.is_capital:
            s = 'Capital wave {0}: '.format(self.wave_id)
        i = 0
        for sl in self.sleepers:
            s += ' '
            s += str(self.sleeper_count[i])
            s += 'x'
            s += str(sl)
            i += 1
        # s += ' [' + self.sleepers_str + ']'
        # stats
        s += ' ['
        s += 'DPS: ' + str(self.total_dps)
        s += ' EHP: ' + str(self.total_ehp)
        s += ' ISK: ' + str(self.total_isk)
        s += '] '
        return s


class WHSignatureGas:
    def __init__(self, name: str, cnt: int):
        self.friendlyName = name.lower()
        self.count = cnt
        self.typeid = 0
        # calculatable
        self.price1piece = 0
        self.volume1piece = 0
        self.total_price = 0
        self.num_pcs_in_venture = 0
        self.full_venture_price = 0
        self.harvest_time_venture_secs = 0
        self.isk_per_hour_venture = 0

    def __str__(self):
        return self.friendlyName + ':' + str(self.count)

    def _calc_typeid_price(self, lp: loot_prices.GasPrices):
        if self.friendlyName == 'c50':
            self.typeid = lp.FULLERITE_C50_ID
            self.price1piece = lp.FULLERITE_C50_PRICE
            self.friendlyName = 'Fullerite-C50'
            self.volume1piece = 1
        elif self.friendlyName == 'c60':
            self.typeid = lp.FULLERITE_C60_ID
            self.price1piece = lp.FULLERITE_C60_PRICE
            self.friendlyName = 'Fullerite-C60'
            self.volume1piece = 1
        elif self.friendlyName == 'c70':
            self.typeid = lp.FULLERITE_C70_ID
            self.price1piece = lp.FULLERITE_C70_PRICE
            self.friendlyName = 'Fullerite-C70'
            self.volume1piece = 1
        elif self.friendlyName == 'c72':
            self.typeid = lp.FULLERITE_C72_ID
            self.price1piece = lp.FULLERITE_C72_PRICE
            self.friendlyName = 'Fullerite-C72'
            self.volume1piece = 2
        elif self.friendlyName == 'c84':
            self.typeid = lp.FULLERITE_C84_ID
            self.price1piece = lp.FULLERITE_C84_PRICE
            self.friendlyName = 'Fullerite-C84'
            self.volume1piece = 2
        elif self.friendlyName == 'c28':
            self.typeid = lp.FULLERITE_C28_ID
            self.price1piece = lp.FULLERITE_C28_PRICE
            self.friendlyName = 'Fullerite-C28'
            self.volume1piece = 2
        elif self.friendlyName == 'c32':
            self.typeid = lp.FULLERITE_C32_ID
            self.price1piece = lp.FULLERITE_C32_PRICE
            self.friendlyName = 'Fullerite-C32'
            self.volume1piece = 5
        elif self.friendlyName == 'c320':
            self.typeid = lp.FULLERITE_C320_ID
            self.price1piece = lp.FULLERITE_C320_PRICE
            self.friendlyName = 'Fullerite-C320'
            self.volume1piece = 5
        elif self.friendlyName == 'c540':
            self.typeid = lp.FULLERITE_C540_ID
            self.price1piece = lp.FULLERITE_C540_PRICE
            self.friendlyName = 'Fullerite-C540'
            self.volume1piece = 10

    def self_recalc(self, lp: loot_prices.GasPrices):
        self._calc_typeid_price(lp)
        self.total_price = round(self.price1piece * self.count)
        total_volume = self.count * self.volume1piece
        full_venture_volume = 5000
        gas_cycleVolume = 80  # Venture 2 x T2 gas harv, Mining Frigate V
        gas_cycleTime = 30  # seconds
        if self.volume1piece > 0:
            self.num_pcs_in_venture = round(full_venture_volume / self.volume1piece)
            self.full_venture_price = round(self.num_pcs_in_venture * self.price1piece)
            pieces_per_cycle = round(gas_cycleVolume / self.volume1piece)
            num_cycles_for_full_venture = self.num_pcs_in_venture // pieces_per_cycle
            self.harvest_time_venture_secs = num_cycles_for_full_venture * gas_cycleTime
            harvest_time_venture_hr = self.harvest_time_venture_secs / 3600  # ~0.5 hours
            #  self.full_venture_price ISK  => harvest_time_venture_hr  hours
            #  ? ISK => 1 hours
            self.isk_per_hour_venture = round((1 / harvest_time_venture_hr) * self.full_venture_price)


class WHSignatureOre:
    def __init__(self, name: str, cnt: int):
        self.friendlyName = name.lower()
        self.count = cnt
        self.typeid = 0
        # get name
        self.name = ''
        self._calc_name()

    def __str__(self):
        return self.name + ':' + str(self.count)

    def _calc_name(self):
        if self.friendlyName == 'ark':
            self.name = 'Arkonor'
            self.typeid = 22
        elif self.friendlyName == 'bis':
            self.name = 'Bistot'
            self.typeid = 1223
        elif self.friendlyName == 'cro':
            self.name = 'Crokite'
            self.typeid = 1225
        elif self.friendlyName == 'dar':
            self.name = 'Dark Ochre'
            self.typeid = 1232
        elif self.friendlyName == 'gne':
            self.name = 'Gneiss'
            self.typeid = 1229
        elif self.friendlyName == 'hed':
            self.name = 'Hedbergite'
            self.typeid = 21
        elif self.friendlyName == 'hem':
            self.name = 'Hemorphite'
            self.typeid = 1231
        elif self.friendlyName == 'jas':
            self.name = 'Jaspet'
            self.typeid = 1226
        elif self.friendlyName == 'ker':
            self.name = 'Kernite'
            self.typeid = 20
        elif self.friendlyName == 'mer':
            self.name = 'Mercoxit'
            self.typeid = 11396
        elif self.friendlyName == 'omb':
            self.name = 'Omber'
            self.typeid = 1227
        elif self.friendlyName == 'pla':
            self.name = 'Plagioclase'
            self.typeid = 18
        elif self.friendlyName == 'pyr':
            self.name = 'Pyroxeres'
            self.typeid = 1224
        elif self.friendlyName == 'sco':
            self.name = 'Scordite'
            self.typeid = 1228
        elif self.friendlyName == 'spo':
            self.name = 'Spodumain'
            self.typeid = 19
        elif self.friendlyName == 'vel':
            self.name = 'Veldspar'
            self.typeid = 1230


class WHSignature:
    def __init__(self, config: sitecfg.SiteConfig):
        self.sig_id = 0
        self.sig_type = ''
        self.wh_class = 0
        self.name = ''
        self.waves = []
        self.has_capital_waves = False
        self.gas_clouds = []
        self.ore_rocks = []
        # statistics (calculatable)
        self.total_ehp = 0
        self.total_isk = 0
        self.isk_per_ehp = 0
        self.isk_per_hour_per_100dps = 0
        self.isk_per_hour_per_500dps = 0
        # loot prices
        self._config = config
        self.priceData = loot_prices.GasPrices()
        self.total_isk_oregas = 0

    def load(self, sig_id: int, db: database.SiteDb):
        self.sig_id = sig_id
        if self.sig_id == 0:
            return
        row = db.query_signature(self.sig_id)
        #  id, wh_class, sig_type, sig_name
        if row:
            self.wh_class = row[1]
            self.sig_type = row[2]
            self.name = row[3]
            sig_rows = db.query_signature_waves(self.sig_id)
            for sig_row in sig_rows:
                wave = WHSignatureWave(self.sig_id)
                wave.initfromrow(sig_row)
                #  wave = WHSignatureWave(0) # hint
                wave.load_sleepers(db)
                wave.calc_stats()
                if wave.is_capital:
                    self.has_capital_waves = True
                # save wave
                self.waves.append(wave)
                # collect stats
                if not wave.is_capital:
                    self.total_ehp += wave.total_ehp
                    self.total_isk += wave.total_isk
            if self.total_ehp > 0:
                self.isk_per_ehp = round(self.total_isk / self.total_ehp)
            # total_profit / total_EHP * 3600 sec * 100dps
            self.isk_per_hour_per_100dps = round(self.isk_per_ehp * 3600 * 100)
            self.isk_per_hour_per_500dps = round(self.isk_per_ehp * 3600 * 500)
            # load ore/gas values
            if self.is_oregas():
                self.priceData.load_prices(self._config)
                oregas_list = db.query_signature_oregas(self.sig_id)
                if self.sig_type == 'gas':
                    # [{'type': 'c50', 'cnt': 3000}, {'type': 'c60', 'cnt': 1500}]
                    for an_oregas in oregas_list:
                        gas1 = WHSignatureGas(an_oregas['type'], an_oregas['cnt'])
                        gas1.self_recalc(self.priceData)
                        self.total_isk_oregas += gas1.total_price
                        if gas1.count > 0:
                            self.gas_clouds.append(gas1)
                elif self.sig_type == 'ore':
                    # [{'type': 'ark', 'cnt': 3}, {'type': 'bis', 'cnt': 3}, ...]
                    for an_oregas in oregas_list:
                        ore1 = WHSignatureOre(an_oregas['type'], an_oregas['cnt'])
                        if ore1.count > 0:
                            self.ore_rocks.append(ore1)
                # count Ore/Gas profit to total profut
                self.total_isk += self.total_isk_oregas
        else:
            self.sig_id = 0

    def is_valid(self):
        if (self.sig_id > 0) and (self.name != ''):
            return True
        return False

    def is_oregas(self):
        if (self.sig_type == 'ore') or (self.sig_type == 'gas'):
            return True
        return False

    def is_ore(self):
        if self.sig_type == 'ore':
            return True
        return False

    def is_gas(self):
        if self.sig_type == 'gas':
            return True
        return False

    def __str__(self):
        s = '<WH Signature'
        if self.sig_id > 0:
            s += ': '
            s += self.name
            if self.sig_type != '':
                s += ', '
                s += self.sig_type
                s += ','
            s += ' (#'
            s += str(self.sig_id)
            s += ')'
        s += '>'
        return s
