# -*- coding: utf-8 -*-
from . import database
from . import loot_prices


class WHSleeper:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.icon = ''
        self.size = ''
        self.wh_class_str = ''
        self.wh_classes = []
        self.signature = 0
        self.maxspeed = 0
        self.orbit = 0
        self.armor = 0
        self.hull = 0
        self.res_em = 0
        self.res_therm = 0
        self.res_kin = 0
        self.res_exp = 0
        self.optimal = 0
        self.dps_em = 0
        self.dps_therm = 0
        self.dps_kin = 0
        self.dps_exp = 0
        self.loot_acd = 0
        self.loot_nna = 0
        self.loot_sdl = 0
        self.loot_sdai = 0
        self.ability_str = ''
        self.abilities = []
        self.is_trigger = False
        self.count = 0
        # calculatable
        self.dps_total = 0
        self.ehp_total = 0
        self.loot_total = 0
        self.isk_per_ehp = 0

    def __str__(self):
        s = 'Sleeper'
        if self.name != '':
            s = self.name
        if self.size != '':
            s += ' (' + self.size + ')'
        if len(self.abilities) > 0:
            s += ' ['
            for ability in self.abilities:
                s += ' ' + ability
            s += ']'
        if self.is_trigger:
            s += ' TRIGGER'
        return s

    def is_valid(self):
        if (self.id> 0) and (self.name != '') and (self.size != ''):
            return True
        return False

    def load_info(self, sleeper_id: int, db: database.SiteDb):
        self.id = int(sleeper_id)
        if self.id == 0:
            return
        row = db.query_sleeper_by_id(self.id)
        if row is None:
            self.id = 0
            return
        self.wh_class_str = row[1]
        self.size = row[2]
        self.name = row[3]
        self.signature = int(row[4])
        self.maxspeed = int(row[5])
        self.orbit = int(row[6])
        self.armor = int(row[7])
        self.hull = int(row[8])
        self.res_em = int(row[9])
        self.res_therm = int(row[10])
        self.res_kin = int(row[11])
        self.res_exp = int(row[12])
        self.optimal = int(row[13])
        self.dps_em = int(row[14])
        self.dps_therm = int(row[15])
        self.dps_kin = int(row[16])
        self.dps_exp = int(row[17])
        self.loot_acd = int(row[18])
        self.loot_nna = int(row[19])
        self.loot_sdl = int(row[20])
        self.loot_sdai = int(row[21])
        self.ability_str = row[22]
        # parse
        self.wh_classes = []
        whcs = self.wh_class_str.split(',')
        for c in whcs:
            self.wh_classes.append(int(c))
        if self.ability_str is not None:
            self.abilities = self.ability_str.split(',')
        self.icon = self.name.lower() + '.png'
        # calc
        self.dps_total = self.dps_em + self.dps_therm + self.dps_kin + self.dps_exp
        armor_average_resist = (self.res_em + self.res_therm + self.res_kin + self.res_exp) / 4
        armor_ehp = round(self.armor / (1 - armor_average_resist/100))
        self.ehp_total = armor_ehp + self.hull
        # loot
        self.loot_total = self.loot_acd * loot_prices.ACD_PRICE
        self.loot_total += self.loot_nna * loot_prices.NNA_PRICE
        self.loot_total += self.loot_sdl * loot_prices.SDL_PRICE
        self.loot_total += self.loot_sdai * loot_prices.SDAI_PRICE
        self.isk_per_ehp = self.loot_total / self.ehp_total

    def set_abilities_from_wave(self, abilities_code: str):
        """
        Sets sleepers abilities from coded str:
        :param abilities_code: 'wndrt'-like string,
               'w' - web, 'n' - neut, 'd' - warp disruptor,
               'r' - remote rep, 't' - next wave trigger
        :return: None
        """
        if abilities_code is None:
            return False
        if abilities_code == '':
            return False
        self.abilities = []
        self.ability_str = ''
        self.is_trigger = False
        #  'wndrt' for: web, neut, dis, rr, trigger
        for c in abilities_code:
            if c == 'w':
                self.ability_str += 'web,'
                self.abilities.append('web')
            elif c == 'n':
                self.ability_str += 'neut,'
                self.abilities.append('neut')
            elif c == 'd':
                self.ability_str += 'dis,'
                self.abilities.append('dis')
            elif c == 'r':
                self.ability_str += 'rr,'
                self.abilities.append('rr')
            elif c == 't':
                self.is_trigger = True
        return True

    def set_count(self, c: int):
        self.count = c
