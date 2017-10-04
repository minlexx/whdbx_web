# -*- coding: utf-8 -*-
from . import database
from . import loot_prices


class WHSleeper:
    def __init__(self):
        self.id = 0
        self.typeid = 0
        self.name = ''
        self.icon = ''
        self.size = ''
        self.wh_class_str = ''
        self.wh_classes = []
        self.signature = 0
        self.maxspeed = 0
        self.orbit = 0
        self.shield = 0
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
        ret = db.query_sleeper_by_id(self.id)
        if ret is None:
            self.id = 0
            return
        self.typeid       = ret['typeid']
        self.wh_class_str = ret['wh_class']
        self.size         = ret['icon']
        self.name         = ret['name']
        self.signature    = ret['signature']
        self.maxspeed     = ret['maxspeed']
        self.orbit        = ret['orbit']
        self.optimal      = ret['optimal']
        self.shield       = ret['shield']
        self.armor        = ret['armor']
        self.hull         = ret['hull']
        self.res_em       = ret['res_em']
        self.res_therm    = ret['res_therm']
        self.res_kin      = ret['res_kin']
        self.res_exp      = ret['res_exp']
        self.dps_em       = ret['dps_em']
        self.dps_therm    = ret['dps_therm']
        self.dps_kin      = ret['dps_kin']
        self.dps_exp      = ret['dps_exp']
        self.loot_acd     = ret['loot_acd']
        self.loot_nna     = ret['loot_nna']
        self.loot_sdl     = ret['loot_sdl']
        self.loot_sdai    = ret['loot_sdai']
        self.ability_str  = ret['ability']
        # parse
        self.wh_classes = []
        whcs = self.wh_class_str.split(',')
        for c in whcs:
            self.wh_classes.append(int(c))
        if self.ability_str is not None:
            self.abilities = self.ability_str.split(',')
        self.icon = self.name.lower() + '.png'
        # calc
        # TODO: include shield resists? none in database yet :(
        self.dps_total = self.dps_em + self.dps_therm + self.dps_kin + self.dps_exp
        armor_average_resist = (self.res_em + self.res_therm + self.res_kin + self.res_exp) / 4
        armor_ehp = round(self.armor / (1 - armor_average_resist/100))
        self.ehp_total = armor_ehp + self.hull + self.shield
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
