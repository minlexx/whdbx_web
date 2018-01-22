# -*- coding: utf-8 -*-
from . import database
from . import loot_prices


class WHSleeper:
    def __init__(self):
        self.id = 0  # primary key in sleepers table
        self.typeid = 0  # eve typeID
        self.name = ''
        self.icon_file = ''
        self.icon = ''
        self.wh_class_str = ''
        self.wh_classes = []
        self.signature = 0
        self.maxspeed = 0
        self.orbit = 0
        self.shield = 0
        self.armor = 0
        self.hull = 0
        self.shield_res_em = 0
        self.shield_res_therm = 0
        self.shield_res_kin = 0
        self.shield_res_exp = 0
        self.armor_res_em = 0
        self.armor_res_therm = 0
        self.armor_res_kin = 0
        self.armor_res_exp = 0
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
        # ewar stats
        self.neut_range = 0
        self.neut_amount = 0
        self.neut_duration = 0
        self.dis_range = 0
        self.dis_strength = 0
        self.web_range = 0
        self.web_strength = 0
        self.rr_range = 0
        self.rr_amount = 0
        self.rr_duration = 0
        self.extra_comment = ''
        # for wave in signature
        self.is_trigger = False
        self.is_random_spawn = False
        self.is_anomaly_despawn_trigger = False
        self.is_decloaked_container_trigger = False
        self.count = 0
        # calculatable
        self.dps_total = 0
        self.ehp_total = 0
        self.loot_total = 0
        self.isk_per_ehp = 0
        self.neut_per_second = 0
        self.rr_per_second = 0

    def __str__(self):
        s = 'Sleeper'
        if self.name != '':
            s = self.name
        if self.icon != '':
            s += ' (' + self.icon + ')'
        if len(self.abilities) > 0:
            s += ' ['
            for ability in self.abilities:
                s += ' ' + ability
            s += ']'
        if self.is_trigger:
            s += ' TRIGGER'
        return s

    def is_valid(self):
        if (self.id > 0) and (self.name != '') and (self.icon != ''):
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
        self.typeid = ret['typeid']
        self.wh_class_str = ret['wh_class']
        self.icon = ret['icon']
        self.name = ret['name']
        self.signature = ret['signature']
        self.maxspeed = ret['maxspeed']
        self.orbit = ret['orbit']
        self.optimal = ret['optimal']
        self.shield = ret['shield']
        self.armor = ret['armor']
        self.hull = ret['hull']
        self.shield_res_em = ret['shield_res_em']
        self.shield_res_therm = ret['shield_res_therm']
        self.shield_res_kin = ret['shield_res_kin']
        self.shield_res_exp = ret['shield_res_exp']
        self.armor_res_em = ret['armor_res_em']
        self.armor_res_therm = ret['armor_res_therm']
        self.armor_res_kin = ret['armor_res_kin']
        self.armor_res_exp = ret['armor_res_exp']
        self.dps_em = ret['dps_em']
        self.dps_therm = ret['dps_therm']
        self.dps_kin = ret['dps_kin']
        self.dps_exp = ret['dps_exp']
        self.loot_acd = ret['loot_acd']
        self.loot_nna = ret['loot_nna']
        self.loot_sdl = ret['loot_sdl']
        self.loot_sdai = ret['loot_sdai']
        self.ability_str = ret['ability']
        # ewar abilities stats
        self.neut_range = ret['neut_range']
        self.neut_amount = ret['neut_amount']
        self.neut_duration = ret['neut_duration']
        self.dis_range = ret['dis_range']
        self.dis_strength = ret['dis_strength']
        self.web_range = ret['web_range']
        self.web_strength = ret['web_strength']
        self.rr_range = ret['rr_range']
        self.rr_amount = ret['rr_amount']
        self.rr_duration = ret['rr_duration']
        self.extra_comment = ret['extra_comment']
        # parse
        self.wh_classes = []
        whcs = self.wh_class_str.split(',')
        for c in whcs:
            self.wh_classes.append(int(c))
        if self.ability_str is not None:
            self.abilities = self.ability_str.split(',')
        # icon file
        self.icon_file = self.name.lower() + '.png'
        # calc
        self.dps_total = self.dps_em + self.dps_therm + self.dps_kin + self.dps_exp
        # calc EHP
        armor_average_resist = (self.armor_res_em + self.armor_res_therm +
                                self.armor_res_kin + self.armor_res_exp) / 4
        shield_average_resist = (self.shield_res_em + self.shield_res_therm +
                                 self.shield_res_kin + self.shield_res_exp) / 4
        armor_ehp = round(self.armor / (1 - armor_average_resist/100))
        shield_ehp = round(self.shield / (1 - shield_average_resist / 100))
        self.ehp_total = shield_ehp + armor_ehp + self.hull
        # loot
        self.loot_total = self.loot_acd * loot_prices.ACD_PRICE
        self.loot_total += self.loot_nna * loot_prices.NNA_PRICE
        self.loot_total += self.loot_sdl * loot_prices.SDL_PRICE
        self.loot_total += self.loot_sdai * loot_prices.SDAI_PRICE
        self.isk_per_ehp = self.loot_total / self.ehp_total
        # ewar stats
        if self.neut_duration > 0:
            self.neut_per_second = round(self.neut_amount / self.neut_duration)
        if self.rr_duration > 0:
            self.rr_per_second = round(self.rr_amount / self.rr_duration)

    def set_abilities_from_wave(self, abilities_code: str):
        """
        Sets sleepers abilities from coded str:
        :param abilities_code: 'wndrt'-like string,
               'w' - web,
               'n' - neut,
               'd' - warp disruptor,
               's' - warp scrambler
               'r' - remote rep,
               't' - next wave trigger,
               'R' - random spawn,
               'Z' - anomaly despawn trigger,
               'D' - decloaked container trigger
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
            elif c == 's':
                self.ability_str += 'scram,'
                self.abilities.append('scram')
            elif c == 'r':
                self.ability_str += 'rr,'
                self.abilities.append('rr')
            elif c == 't':
                self.is_trigger = True
            elif c == 'R':
                self.is_random_spawn = True
            elif c == 'Z':
                self.is_anomaly_despawn_trigger = True
            elif c == 'D':
                self.is_decloaked_container_trigger = True
        return True

    def set_count(self, c: int):
        self.count = c
