# -*- coding: utf-8 -*-
from enum import IntEnum
import json
import sqlite3
import threading

from . import sitecfg


# WH class value constants
class WHClass(IntEnum):
    HISEC_WH_CLASS = 7
    LOW_WH_CLASS = 8
    NULL_WH_CLASS = 9
    THERA_WH_CLASS = 12
    FRIG_WH_CLASS = 13
    DRIFTERS_WH_CLASS_MIN = 14
    DRIFTERS_WH_CLASS_MAX = 18

    @staticmethod
    def is_drifters(cl: int) -> bool:
        if (cl >= WHClass.DRIFTERS_WH_CLASS_MIN) and (cl <= WHClass.DRIFTERS_WH_CLASS_MAX):
            return True
        return False

    @staticmethod
    def is_shattered(cl: int) -> bool:
        if (cl <= -1) and (cl >= -6):
            return True
        return False

    @staticmethod
    def is_frig_shattered(cl: int) -> bool:
        if cl == WHClass.FRIG_WH_CLASS:
            return True
        return False

    @staticmethod
    def is_thera(cl: int) -> bool:
        if cl == WHClass.THERA_WH_CLASS:
            return True
        return False

    @staticmethod
    def to_string(cl: int) -> str:
        if cl == WHClass.HISEC_WH_CLASS: return 'hi sec'
        if cl == WHClass.LOW_WH_CLASS: return 'low sec'
        if cl == WHClass.NULL_WH_CLASS: return 'null sec'
        if WHClass.is_thera(cl): return 'Thera'
        s = 'c' + str(abs(cl))  # 'c4' / 'c13'
        if WHClass.is_shattered(cl):
            s += ' shattered'
        elif WHClass.is_frig_shattered(cl):
            s += ' frig shattered'
        elif WHClass.is_drifters(cl):
            s += ' drifters WH'
        return s


def safe_int(v) -> int:
    if v is None:
        return None
    return int(v)


def safe_float(v) -> float:
    if v is None:
        return None
    return float(v)


def get_ss_security_color(security_level: float) -> str:
    sec_color = '#ff0000'
    sec_colors = dict()
    sec_colors['1.0'] = '#33ffff'
    sec_colors['0.9'] = '#4cffcc'
    sec_colors['0.8'] = '#00ff4c'
    sec_colors['0.7'] = '#00ff00'
    sec_colors['0.6'] = '#99ff33'
    sec_colors['0.5'] = '#ffff00'
    sec_colors['0.4'] = '#e57f00'
    sec_colors['0.3'] = '#ff6600'
    sec_colors['0.2'] = '#ff4c00'
    sec_colors['0.1'] = '#e53300'
    sec_colors['0.0'] = '#ff0000'
    if security_level >= 1.0:
        sec_color = sec_colors['1.0']
    elif security_level >= 0.9:
        sec_color = sec_colors['0.9']
    elif security_level >= 0.8:
        sec_color = sec_colors['0.8']
    elif security_level >= 0.7:
        sec_color = sec_colors['0.7']
    elif security_level >= 0.6:
        sec_color = sec_colors['0.6']
    elif security_level >= 0.5:
        sec_color = sec_colors['0.5']
    elif security_level >= 0.4:
        sec_color = sec_colors['0.4']
    elif security_level >= 0.3:
        sec_color = sec_colors['0.3']
    elif security_level >= 0.2:
        sec_color = sec_colors['0.2']
    elif security_level >= 0.1:
        sec_color = sec_colors['0.1']
    elif security_level <= 0.0:
        sec_color = sec_colors['0.0']
    return sec_color


class SiteDb:
    def __init__(self, siteconfig: sitecfg.SiteConfig):
        self._conn = sqlite3.connect(siteconfig.EVEDB, check_same_thread=False)
        # vars for route finding
        self._jumps_cache = dict()  # db cache
        self._jumps_max_jumps = 0
        self._jumps_min_route_len = 9999
        self._routes_cache_dir = siteconfig.ROUTES_CACHE_DIR
        self._write_lock = threading.Lock()

    def connection_handle(self):
        return self._conn

    def query_hole_info(self, hole: str) -> tuple:
        cur = self._conn.cursor()
        q = 'SELECT in_class, maxStableTime, maxStableMass, ' \
            '       maxJumpMass, massRegeneration ' \
            ' FROM wormholeclassifications WHERE hole = ?'
        cur.execute(q, (hole,))
        row = cur.fetchone()
        cur.close()
        return row

    def query_effect_info(self, effect_id: int, effect_class: int) -> list:
        query = 'SELECT effect, icon, c{0} ' \
                'FROM effects_new WHERE id_type = ?'.format(effect_class)
        cursor = self._conn.cursor()
        cursor.execute(query, (effect_id,))
        effects = list()
        for row in cursor:
            effects.append(row)
        cursor.close()
        return effects

    def query_wormholesystem(self, ssys_id: int) -> tuple:
        select_wh_query = (
            'SELECT class, star, planet, moon, effect, static_1, static_2 '
            'FROM wormholesystems WHERE solarsystemid = ?')
        cursor = self._conn.cursor()
        cursor.execute(select_wh_query, (ssys_id, ))
        row = cursor.fetchone()
        return row

    def query_wormholesystem_new(self, ssys_id: int) -> tuple:
        select_wh_query_new = (
            'SELECT class, star, planets, moons, effect, statics '
            'FROM wormholesystems_new WHERE solarsystemid = ?')
        cursor = self._conn.cursor()
        cursor.execute(select_wh_query_new, (ssys_id, ))
        row = cursor.fetchone()
        return row

    def set_wormholesystem_statics(self, ssys_id: int, statics_str: str):
        select_wh_query_new = (
            'UPDATE wormholesystems_new SET statics = ? '
            ' WHERE solarsystemid = ?')
        # get write lock
        self._write_lock.acquire()
        #
        cursor = self._conn.cursor()
        cursor.execute(select_wh_query_new, (statics_str, ssys_id))
        self._conn.commit()
        cursor.close()
        # release lock
        self._write_lock.release()

    def query_solarsystem(self, ssys_id: int) -> tuple:
        ccp_q = (
            'SELECT ss.solarSystemName, ss.security, ss.radius, ss.regionID, '
            '       ss.constellationID, mr.itemName as regionName, mc.itemName as constellationName '
            ' FROM mapsolarsystems ss '
            ' JOIN mapdenormalize mr ON mr.itemID = ss.regionID '
            ' JOIN mapdenormalize mc ON mc.itemID = ss.constellationID '
            'WHERE ss.solarsystemid = ?')
        cursor = self._conn.cursor()
        cursor.execute(ccp_q, (ssys_id, ))
        row = cursor.fetchone()
        return row

    def query_solarsystem_planets(self, ssid: int) -> list:
        ret = []
        q = 'SELECT ss.solarSystemName as ssname, ' \
            '       mc.constellationName as constname, ' \
            '       mr.regionName as regname, ' \
            '       ss.security as security, ' \
            '       round(ss.radius/149600000000,2) as radius, ' \
            '       md.itemName as Object, it.typeName as ObjectDescription '\
            'FROM mapSolarSystems ss ' \
            'JOIN mapRegions mr ON mr.regionID=ss.regionID ' \
            'JOIN mapConstellations mc ON mc.constellationID=ss.constellationID ' \
            'JOIN mapDenormalize md ON md.solarSystemID=ss.solarSystemID ' \
            'JOIN invTypes it ON (it.typeID=md.typeID AND it.groupID=7) ' \
            'WHERE ss.solarSystemID=?'
        cursor = self._conn.cursor()
        if cursor.execute(q, (ssid, )):
            for row in cursor.fetchall():
                t = (row[5], row[6])  # ('J165806 I', 'Planet (Lava)')
                ret.append(t)
        return ret

    def select_all_sleepers(self) -> list:
        ret = list()
        q = 'SELECT id,name FROM sleepers ORDER BY id'
        cur = self._conn.cursor()
        cur.execute(q)
        for row in cur:
            s = dict()
            s['id'] = int(row[0])
            s['name'] = row[1]
            s['icon'] = str(row[1]).lower() + '.png'
            ret.append(s)
        return ret

    def select_all_effects(self) -> list:
        ret = list()
        q = 'SELECT id,id_type,hole,effect,icon,c1,c2,c3,c4,c5,c6 FROM effects_new ORDER BY id'
        cur = self._conn.cursor()
        cur.execute(q)
        for row in cur:
            s = dict()
            s['id'] = int(row[0])
            s['id_type'] = int(row[1])
            s['name'] = row[2]
            s['effect'] = row[3]
            s['icon'] = row[4]
            s['c1'] = row[5]
            s['c2'] = row[6]
            s['c3'] = row[7]
            s['c4'] = row[8]
            s['c5'] = row[9]
            s['c6'] = row[10]
            ret.append(s)
        return ret

    def query_sleeper_by_id(self, sleeper_id: int) -> dict:
        sleeper_query = (
            'SELECT id, typeid, wh_class, icon, name,'    # 0..4
            ' signature, maxspeed, orbit, optimal, '      # 5..8
            ' shield, armor, hull, '                        # 9..11
            ' shield_res_em, shield_res_therm, shield_res_kin, shield_res_exp, '  # 12..15
            ' armor_res_em, armor_res_therm, armor_res_kin, armor_res_exp, '      # 16..19
            ' dps_em, dps_therm, dps_kin, dps_exp,'       # 20..23
            ' loot_acd, loot_nna, loot_sdl, loot_sdai, '  # 24..27
            ' ability, '                                      # 28
            ' neut_range, neut_amount, neut_duration, '   # 29..31
            ' dis_range, dis_strength, '                   # 32, 33
            ' web_range, web_strength, '                  # 34, 35
            ' rr_range, rr_amount, rr_duration, '       # 36..38
            ' extra_comment '                            # 39
            'FROM sleepers WHERE id = ?')
        cursor = self._conn.cursor()
        cursor.execute(sleeper_query, (sleeper_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        ret = {
            'id': int(row[0]),
            'typeid': int(row[1]),
            'wh_class': str(row[2]),
            'icon': str(row[3]),
            'name': str(row[4]),
            'signature': int(row[5]),
            'maxspeed': int(row[6]),
            'orbit': int(row[7]),
            'optimal': int(row[8]),
            'shield': int(row[9]),
            'armor': int(row[10]),
            'hull': int(row[11]),
            'shield_res_em': int(row[12]),
            'shield_res_therm': int(row[13]),
            'shield_res_kin': int(row[14]),
            'shield_res_exp': int(row[15]),
            'armor_res_em': int(row[16]),
            'armor_res_therm': int(row[17]),
            'armor_res_kin': int(row[18]),
            'armor_res_exp': int(row[19]),
            'dps_em': int(row[20]),
            'dps_therm': int(row[21]),
            'dps_kin': int(row[22]),
            'dps_exp': int(row[23]),
            'loot_acd': int(row[24]),
            'loot_nna': int(row[25]),
            'loot_sdl': int(row[26]),
            'loot_sdai': int(row[27]),
            'ability': row[28],  # may be None, let it be None, not 'None'
            'neut_range': int(row[29]),
            'neut_amount': int(row[30]),
            'neut_duration': int(row[31]),
            'dis_range': int(row[32]),
            'dis_strength': int(row[33]),
            'web_range': int(row[34]),
            'web_strength': int(row[35]),
            'rr_range': int(row[36]),
            'rr_amount': int(row[37]),
            'rr_duration': int(row[38]),
            'extra_comment': str(row[39])
        }
        return ret

    def query_sleeper_by_class(self, class_str: str) -> list:
        ret = []
        sleeper_query = (
            'SELECT id, typeid, wh_class, icon, name FROM sleepers WHERE wh_class = ?')
        cur = self._conn.cursor()
        cur.execute(sleeper_query, (class_str,))
        for row in cur:
            sl = {
                'id': int(row[0]),
                'typeid': int(row[1]),
                'wh_class_str': str(row[2]),
                'icon': str(row[3]),
                'name': str(row[4])
            }
            ret.append(sl)
        return ret

    def postprocess_signatures_calc_max_dps(self, sigs_list: list) -> None:
        # for each signature, get all waves
        #  for each wave, parse sleepers line
        #   for each sleeper get is dps
        #   sum all sleepers dps in this wave
        #   remember maximum wave dps
        for sig in sigs_list:
            max_dps = 0
            waves = self.query_signature_waves(sig['id'])
            for wave in waves:
                total_wave_dps = 0
                is_capital = int(wave[2])
                if is_capital:  # skip capital waves
                    continue
                sleepers_str = str(wave[3])
                # parse sleepers str
                sl_defs = sleepers_str.split(',')
                for sl_def in sl_defs:
                    #  'sleeper_id:count:abilities' or 'sleeper_id:count'
                    sl_def = sl_def.strip()
                    sl_def_list = sl_def.split(':')
                    sl_id = int(sl_def_list[0])
                    if sl_id > 0:
                        sl_count = int(sl_def_list[1])
                        # we have sleeper ID and its count
                        sl_info = self.query_sleeper_by_id(sl_id)
                        if sl_info is not None:
                            sleeper_dps = sl_info['dps_em'] + sl_info['dps_therm'] \
                                          + sl_info['dps_kin'] + sl_info['dps_exp']
                            total_wave_dps += sleeper_dps * sl_count
                if total_wave_dps > max_dps:
                    max_dps = total_wave_dps
            sig['max_dps'] = max_dps

    def query_signatures_for_class(self, wh_class: int, calc_max_dps: bool = False) -> list:
        ret = []
        q = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE wh_class = ?'
        cur = self._conn.cursor()
        cur.execute(q, (wh_class,))
        for row in cur:
            sig = dict()
            sig['id'] = int(row[0])
            sig['wh_class'] = int(row[1])
            sig['sig_type'] = row[2]
            sig['sig_name'] = row[3]
            sig['max_dps'] = 0
            ret.append(sig)
        cur.close()
        # don't forget about shattered!
        if (wh_class >= -6) and (wh_class <= -1):
            qwhcl = (-1) * wh_class
            cur = self._conn.cursor()
            cur.execute(q, (qwhcl,))
            for row in cur:
                sig = dict()
                sig['id'] = int(row[0])
                sig['wh_class'] = int(row[1])
                sig['sig_type'] = row[2]
                sig['sig_name'] = row[3]
                sig['max_dps'] = 0
                ret.append(sig)
            cur.close()
        # thera also has class 3/4 sigs
        # if wh_class == self.THERA_WH_CLASS:
        #    q34 = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE wh_class=3 OR wh_class=4'
        #    cur = self._conn.cursor()
        #    cur.execute(q34)
        #    for row in cur:
        #        sig = dict()
        #        sig['id'] = int(row[0])
        #        sig['wh_class'] = int(row[1])
        #        sig['sig_type'] = row[2]
        #        sig['sig_name'] = row[3]
        #        ret.append(sig)
        #    cur.close()
        # ^^ do not do it - too many lines there
        #
        # frig WHs contain class 1-3 anomalies
        if wh_class == WHClass.FRIG_WH_CLASS:
            q_frig = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE wh_class=3'
            cur = self._conn.cursor()
            cur.execute(q_frig)
            for row in cur:
                sig = dict()
                sig['id'] = int(row[0])
                sig['wh_class'] = int(row[1])
                sig['sig_type'] = row[2]
                sig['sig_name'] = row[3]
                sig['max_dps'] = 0
                ret.append(sig)
            cur.close()
        if calc_max_dps:
            self.postprocess_signatures_calc_max_dps(ret)
        return ret

    def query_gas_signatures(self, calc_max_dps: bool = False) -> list:
        ret = []
        q = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE sig_type = ?'
        cur = self._conn.cursor()
        cur.execute(q, ('gas',))
        for row in cur:
            sig = dict()
            sig['id'] = int(row[0])
            sig['wh_class'] = int(row[1])
            sig['sig_type'] = row[2]
            sig['sig_name'] = row[3]
            sig['max_dps'] = 0
            ret.append(sig)
        if calc_max_dps:
            self.postprocess_signatures_calc_max_dps(ret)
        return ret

    def query_ore_signatures(self, calc_max_dps: bool = False) -> list:
        ret = []
        q = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE sig_type = ?'
        cur = self._conn.cursor()
        cur.execute(q, ('ore',))
        for row in cur:
            sig = dict()
            sig['id'] = int(row[0])
            sig['wh_class'] = int(row[1])
            sig['sig_type'] = row[2]
            sig['sig_name'] = row[3]
            sig['max_dps'] = 0
            ret.append(sig)
        if calc_max_dps:
            self.postprocess_signatures_calc_max_dps(ret)
        return ret

    def query_signature(self, sig_id: int) -> tuple:
        sig_query = 'SELECT id,wh_class,sig_type,sig_name FROM signatures WHERE id = ?'
        cur = self._conn.cursor()
        cur.execute(sig_query, (sig_id,))
        row = cur.fetchone()
        return row

    def query_signature_waves(self, sig_id: int) -> list:
        ret = []
        sig_waves_query = 'SELECT sig_id,wave_id,is_capital,sleepers FROM signature_waves WHERE sig_id = ?'
        cur = self._conn.cursor()
        cur.execute(sig_waves_query, (sig_id,))
        for row in cur:
            ret.append(row)
        return ret

    def query_signature_oregas(self, sig_id: int) -> list:
        ret = list()
        sig_oregas_query = 'SELECT sig_id, oregas FROM signature_oregas WHERE sig_id = ?'
        cur = self._conn.cursor()
        cur.execute(sig_oregas_query, (sig_id,))
        row = cur.fetchone()
        if row:
            oregas = row[1]  # oregas = 'c50:3000,c60:1500'
            # 'ark:3,bis:3,cro:20,dar:4,gne:5,hed:10,hem:20,jas:10,ker:20,omb:15,pla:10,pyr:1,sco:6,spo:10,vel:30'
            if oregas is not None:
                if oregas != '':
                    oregas_parts = oregas.split(',')
                    for oregas_part in oregas_parts:
                        # oregas_part = 'c50:3000'
                        if oregas_part != '':
                            gt_gc = oregas_part.split(':')
                            if len(gt_gc) == 2:
                                og = dict()
                                og['type'] = gt_gc[0]
                                og['cnt'] = int(gt_gc[1])
                                ret.append(og)
        # ret will be like: [{'type': 'c50', 'cnt': 3000}, {'type': 'c60', 'cnt': 1500}]
        return ret

    def jumps_from_system(self, from_ss: int) -> dict:
        if self._jumps_cache:
            if from_ss in self._jumps_cache:
                return self._jumps_cache[from_ss]
        ret = list()
        cur = self._conn.cursor()
        q = ('SELECT '
             '  ssj.fromSolarSystemID, ssf.itemName, ssf.security,'
             '  ssj.toSolarSystemID, sst.itemName, sst.security '
             'FROM mapSolarSystemJumps ssj '
             ' JOIN mapDenormalize ssf on ssf.itemID = ssj.fromSolarSystemID '
             ' JOIN mapDenormalize sst on sst.itemID = ssj.toSolarSystemID '
             'WHERE ssj.fromSolarSystemID=?')
        cur.execute(q, (from_ss,))
        for row in cur:
            jump = dict()
            jump['from_ssid'] = int(row[0])
            jump['from_ssname'] = row[1]
            jump['from_sssec'] = float(row[2])
            jump['to_ssid'] = int(row[3])
            jump['to_ssname'] = row[4]
            jump['to_sssec'] = float(row[5])
            ret.append(jump)
        self._jumps_cache[from_ss] = ret
        return ret

    def _print_tab(self, recursion_limit: int, s: str=None):
        tab = ''
        for i in range(0, self._jumps_max_jumps - recursion_limit):
            tab += ' '
        # tab = '(' + str(recursion_limit) + ') '
        print(tab, end='')
        if s:
            print(s)

    def _str_route(self, route: list) -> str:
        ret = ''
        for j in route:
            ret += j['to_ssname'] + ' - '
        return ret

    def _find_route_dive(self, cur_jump: dict, target_ss: int,
                         recursion_limit: int, visited_systems: list, sec_min: float) -> list:
        # check recursion limit
        recursion_limit -= 1
        if recursion_limit <= 0:
            # self.print_tab(recursion_limit, 'dive: STOP: hit recursion limit while jumping to {0}!'.
            #               format(cur_jump['to_ssname']))
            return None
        # if cur_jump['to_ssid'] in visited_systems:
        #    self.print_tab(recursion_limit, 'dive: ERROR: next system ({0}) is already visited!'.
        #                   format(cur_jump['to_ssname']))
        #    return None
        jumps_done = self._jumps_max_jumps - recursion_limit
        if jumps_done > self._jumps_min_route_len:
            # self.print_tab(recursion_limit, 'dive: this route is longer than the previous ({0} > {1}); return None'.
            #               format(jumps_done, self._jumps_min_route_len))
            return None
        # routes
        sub_routes = list()
        # make jumps
        # self.print_tab(recursion_limit, 'dive: JUMP into {0} {1}'.format(cur_jump['to_ssname'], cur_jump['to_ssid']))
        # make internal copy of visited systems list up to this step
        v_systems_copy = list(visited_systems)
        jumps = self.jumps_from_system(cur_jump['to_ssid'])
        for next_jump in jumps:
            # found our target system?
            if next_jump['to_ssid'] == target_ss:
                v_systems_copy.append(next_jump['to_ssid'])
                ret_route = list()
                ret_route.append(next_jump)
                ret_route.append(cur_jump)
                # self.print_tab(recursion_limit, 'dive: TARGET [{0}] system from {1}! {2} jumps: [{3}]'.format(
                #    next_jump['to_ssname'], cur_jump['to_ssname'], len(ret_route), self.str_route(ret_route)))
                jumps_done += 1
                if self._jumps_min_route_len > jumps_done:
                    self._jumps_min_route_len = jumps_done
                return ret_route
            # nope :(
            if next_jump['to_ssid'] not in v_systems_copy:
                if next_jump['to_sssec'] >= sec_min:
                    # RECURSION POWER
                    v_systems_copy.append(next_jump['to_ssid'])
                    route = self._find_route_dive(next_jump, target_ss,
                                                  recursion_limit, v_systems_copy, sec_min)
                    if route:
                        route.append(cur_jump)
                        sub_routes.append(route)
                        # self.print_tab(recursion_limit, 'dive: storing successful target route in {0}'.
                        #                format(cur_jump['to_ssname']))
        # finished jumping from this system, compare routes
        if len(sub_routes) <= 0:
            # self.print_tab(recursion_limit, 'dive: DEADEND: no other jumps from {0} :('.
            #                format(cur_jump['to_ssname']))
            return None
        min_route = sub_routes[0]
        min_route_len = len(sub_routes[0])
        for sub_route in sub_routes:
            rlen = len(sub_route)
            if rlen < min_route_len:
                min_route_len = rlen
                min_route = sub_route
        # self.print_tab(recursion_limit, 'dive: finished jumping, returning from {0}: [{1}]'.
        #                format(cur_jump['to_ssname'], self.str_route(min_route)))
        return min_route

    def find_route(self, from_ss: int, target_ss: int, sec_min: float=0.5, max_jumps=25) -> list:
        # stupid, we are already in target ss
        if from_ss == target_ss:
            return list()  # empty list, 0 jumps route
        #
        self._jumps_max_jumps = max_jumps
        self._jumps_min_route_len = 9999
        routes = list()
        v_systems = list()
        v_systems.append(from_ss)
        jumps = self.jumps_from_system(from_ss)
        for next_jump in jumps:
            if next_jump['to_sssec'] >= sec_min:
                v_systems.append(next_jump['to_ssid'])
                ret = self._find_route_dive(next_jump, target_ss, max_jumps, v_systems, sec_min)
                if ret:
                    ret.reverse()
                    routes.append(ret)
        if len(routes) > 0:
            # print('find_route: found {0} routes:'.format(len(routes)))
            min_route = routes[0]
            min_route_len = len(routes[0])
            for route in routes:
                # print(' - route {0} jumps: {1}'.format(len(route), self._str_route(route)))
                if len(route) < min_route_len:
                    min_route = route
                    min_route_len = len(route)
            return min_route
        return None

    def find_route_cache(self, from_ss: int, target_ss: int, sec_min: float=0.5,
                         max_jumps: int=25, cache_dir: str=None) -> list:
        ret = None
        read_from_cache = False
        if cache_dir is None:
            cache_dir = self._routes_cache_dir
        filename = cache_dir + '/' + str(from_ss) + '_' + str(target_ss) + \
            '_' + str(max_jumps) + '_' + str(sec_min) + '.json'
        try:
            file = open(filename, 'rt')
            txt = file.read()
            file.close()
            ret = json.loads(txt)
            read_from_cache = True
        except IOError as e:
            ret = None
            read_from_cache = False
        if not read_from_cache:
            ret = self.find_route(from_ss, target_ss, sec_min, max_jumps)
            # if ret:  # save eveif route not found, try
            try:
                file = open(filename, 'wt')
                file.write(json.dumps(ret))
                file.close()
            except IOError as e:
                pass
        return ret

    def find_wormhole(self, name: str) -> dict:
        ret = None
        q = 'SELECT id,hole,in_class,maxStableTime,maxStableMass,massRegeneration,maxJumpMass ' \
            ' FROM wormholeclassifications ' \
            ' WHERE hole = ?'
        cur = self._conn.cursor()
        cur.execute(q, (name,))
        row = cur.fetchone()
        if row:
            ret = dict()
            ret['id'] = int(row[0])
            ret['name'] = row[1]
            ret['in_class'] = int(row[2])
            ret['maxStableTime'] = int(row[3])
            ret['maxStableMass'] = int(row[4])
            ret['massRegeneration'] = int(row[5])
            ret['maxJumpMass'] = int(row[6])
        return ret

    def find_ss_by_name(self, name: str) -> dict:
        ret = None
        q = 'SELECT ss.solarSystemID, ss.solarSystemName, ss.security, ss.sunTypeID, ss.regionID, '\
            '   it.typeName, mr.regionName ' \
            ' FROM mapSolarSystems ss ' \
            ' JOIN invTypes it ON it.typeID=ss.sunTypeID ' \
            ' JOIN mapRegions mr ON mr.regionID=ss.regionID ' \
            ' WHERE ss.solarSystemName LIKE ?'
        cur = self._conn.cursor()
        cur.execute(q, (name,))
        row = cur.fetchone()
        if row:
            ret = dict()
            ret['id'] = int(row[0])
            ret['name'] = str(row[1])
            ret['security'] = float(row[2])
            ret['suntypeid'] = int(row[3])
            ret['regionid'] = int(row[4])
            ret['suntype'] = str(row[5])
            ret['regionname'] = str(row[6])
        return ret

    def find_ss_by_id(self, ssid: int) -> dict:
        ret = None
        q = 'SELECT ss.solarSystemID, ss.solarSystemName, ss.security, ss.sunTypeID, ss.regionID, ' \
            '  it.typeName, mr.regionName ' \
            ' FROM mapSolarSystems ss ' \
            ' JOIN invTypes it ON it.typeID=ss.sunTypeID ' \
            ' JOIN mapRegions mr ON mr.regionID=ss.regionID ' \
            ' WHERE ss.solarSystemID=?'
        cur = self._conn.cursor()
        cur.execute(q, (ssid,))
        row = cur.fetchone()
        if row:
            ret = dict()
            ret['id'] = int(row[0])
            ret['name'] = str(row[1])
            ret['security'] = float(row[2])
            ret['suntypeid'] = int(row[3])
            ret['regionid'] = int(row[4])
            ret['suntype'] = str(row[5])
            ret['regionname'] = str(row[6])
        return ret

    def find_solarsystem_planets(self, ssid: int) -> list:
        ret = []
        if ssid <= 0:
            return ret
        q = ('SELECT md.itemID, md.typeID, md.groupID, md.itemName, it.typeName '
             ' FROM mapDenormalize as md '
             ' JOIN invTypes it ON it.typeID=md.typeID '
             ' WHERE md.groupID=7 AND md.solarsystemID=?')
        cur = self._conn.cursor()
        cur.execute(q, (ssid,))
        for row in cur:
            p = dict()
            p['itemid'] = int(row[0])
            p['typeid'] = int(row[1])
            p['groupid'] = int(row[2])
            p['name'] = row[3]
            p['typename'] = row[4]
            ret.append(p)
        return ret

    def find_solarsystem_moons(self, ssid: int) -> list:
        ret = []
        if ssid <= 0:
            return ret
        q = ('SELECT md.itemID, md.typeID, md.groupID, md.itemName, it.typeName '
             ' FROM mapDenormalize as md '
             ' JOIN invTypes it ON it.typeID=md.typeID '
             ' WHERE md.groupID=8 AND md.solarsystemID=?')
        cur = self._conn.cursor()
        cur.execute(q, (ssid,))
        for row in cur:
            p = dict()
            p['itemid'] = int(row[0])
            p['typeid'] = int(row[1])
            p['groupid'] = int(row[2])
            p['name'] = row[3]
            p['typename'] = row[4]
            ret.append(p)
        return ret

    def find_typeid(self, typeid: int) -> dict:
        ret = dict()
        ret['typeid'] = 0
        ret['name'] = ''
        ret['groupid'] = 0
        ret['groupname'] = ''
        ret['capacity'] = 0
        q = 'SELECT it.typeID, it.typeName, it.groupID, ig.groupName, it.capacity ' \
            ' FROM  invTypes it ' \
            ' JOIN invGroups ig ON it.groupID = ig.groupID ' \
            ' WHERE it.typeID = ?'
        try:
            cur = self._conn.cursor()
            cur.execute(q, (typeid,))
            row = cur.fetchone()
            if row:
                ret['typeid'] = typeid
                if row[1] is not None:
                    ret['name'] = row[1]
                if row[2] is not None:
                    ret['groupid'] = int(row[2])
                if row[3] is not None:
                    ret['groupname'] = row[3]
                if row[4] is not None:
                    ret['capacity'] = float(row[4])
        except TypeError as te:
            print('Content-type: text/plain\n\n')
            print('database.find_typeid(): error finding typeID = ', typeid)
            print(str(te))
        return ret

    def map_denormalize(self, itemid: int) -> dict:
        ret = None
        q = 'SELECT itemID, typeID, groupID, solarSystemID, ' \
            ' constellationID, regionID, orbitID, x, y, z, ' \
            ' radius, itemName, security, celestialIndex, orbitIndex ' \
            'FROM mapDenormalize WHERE itemID = ?'
        cur = self._conn.cursor()
        cur.execute(q, (itemid,))
        row = cur.fetchone()
        if row:
            ret = dict()
            ret['itemid'] = safe_int(row[0])
            ret['typeid'] = safe_int(row[1])
            ret['groupid'] = safe_int(row[2])
            ret['solarsystemid'] = safe_int(row[3])
            ret['constellationid'] = safe_int(row[4])
            ret['regionid'] = safe_int(row[5])
            ret['orbitid'] = safe_int(row[6])
            ret['x'] = safe_float(row[7])
            ret['y'] = safe_float(row[8])
            ret['z'] = safe_float(row[9])
            ret['radius'] = safe_float(row[10])
            ret['name'] = str(row[11])
            ret['security'] = safe_float(row[12])
            ret['celestialindex'] = safe_int(row[13])
            ret['orbitindex'] = safe_int(row[14])
        return ret

    def pos_fuel_data(self, pos_typeid: int) -> dict:
        ret = None
        q = 'SELECT typeID, typeName, fuel_bay_capacity, strontium_bay_capacity, fuel_blocks_per_hour ' \
            ' FROM posFuelData WHERE typeID = ?'
        cur = self._conn.cursor()
        cur.execute(q, (pos_typeid,))
        row = cur.fetchone()
        if row:
            ret = dict()
            ret['typeid'] = pos_typeid
            ret['name'] = row[1]
            ret['fuel_bay'] = int(row[2])
            ret['stron_bay'] = int(row[3])
            ret['bph'] = int(row[4])
        return ret


# <loc><url=showinfo:5//30002187>Amarr</url>
# <loc><url=showinfo:5//30000142>Jita</url>
# <loc><url=showinfo:5//30002659>Dodixie</url>
# <loc><url=showinfo:5//30002053>Hek</url>
# <loc><url=showinfo:5//30002510>Rens</url>
# db.find_route(30003067, 30002187)
# db.find_route(30003067, 30000142)

# -- SELECT * FROM mapdenormalize WHERE groupID=3; -- regions
# -- SELECT * FROM mapdenormalize WHERE groupID=4; -- constellations
# -- SELECT * FROM mapdenormalize WHERE groupID=5; -- solarsystems
# -- SELECT * FROM mapdenormalize WHERE groupID=6; -- stars
# -- SELECT * FROM mapdenormalize WHERE groupID=7; -- planets
# -- SELECT * FROM mapdenormalize WHERE groupID=8; -- moons
# -- SELECT * FROM mapdenormalize WHERE groupID=9; -- belts

# huola from mapDenormalize
# select itemID,typeID,itemName from mapDenormalize where itemid=30003067;

# jumps from huola
# SELECT ssj.fromSolarSystemID, ssf.itemName, ssj.toSolarSystemID, sst.itemName, sst.security
#  FROM mapSolarSystemJumps ssj
#  JOIN mapDenormalize ssf on ssf.itemID = ssj.fromSolarSystemID
#  JOIN mapDenormalize sst on sst.itemID = ssj.toSolarSystemID
# WHERE ssj.fromSolarSystemID=30003067;

# planets in thera
# SELECT md.itemID, md.typeID, md.groupID, md.itemName, it.typeName
#  FROM mapDenormalize as md
#  JOIN invTypes it ON it.typeID=md.typeID
# WHERE md.groupID=7 AND md.solarsystemID=31000005;

# wormholesystem with effect name:
# SELECT md.itemID, md.typeID, md.groupID, md.solarSystemID, md.itemName, it.typeName
#  FROM mapDenormalize md
#  JOIN invTypes it ON it.typeID=md.typeID
# WHERE md.solarSystemID=31002604;

# groupID=995 for WH class effects, typeID=30669 for Wolf-Rayet
# groupID categoryID groupName desc iconID
# 995|2|Secondary Sun|Objects making up part of a multi-celestial grouping||0|1|1|0|0|0|0
# category=2 is celestial

# base group IDs
# sqlite> select * from invgroups limit 10;
# groupID categoryID groupName description iconID
# 0|0|#System|||0|1|1|0|0|0|0
# 1|1|Character|||0|1|1|0|0|0|0
# 2|1|Corporation|||0|1|1|0|0|0|0
# 3|2|Region|||0|1|1|0|0|0|0
# 4|2|Constellation|||0|1|1|0|0|0|0
# 5|2|Solar System|||0|1|1|0|0|0|0
# 6|2|Sun|||0|1|1|0|0|0|0
# 7|2|Planet|||0|1|1|0|0|0|0
# 8|2|Moon|||0|1|1|0|0|0|0
# 9|2|Asteroid Belt||15|0|1|1|0|0|0|0
# 32|1|Alliance|||0|1|1|0|0|0|0

# select all wormholes:
# SELECT typeID, groupID, typeName FROM invTypes WHERE groupID=988;
# 34134|988|Wormhole E004
# 34135|988|Wormhole L005
# 34136|988|Wormhole Z006
# 34137|988|Wormhole M001
# 34138|988|Wormhole C008
# 34139|988|Wormhole G008
# 34140|988|Wormhole Q003
# 34338|988|Wormhole T458
# 34366|988|Wormhole M164
# 34367|988|Wormhole L031
# 34368|988|Wormhole Q063
# 34369|988|Wormhole V898
# 34370|988|Wormhole E587
# 34371|988|Wormhole F353
# 34372|988|Wormhole F135
# 34439|988|Wormhole A009

# SELECT attributeID, categoryID, attributeName, description
#   FROM dgmattributetypes
#   WHERE attributeName like '%wormhole%';
# 1381|7|wormholeTargetSystemClass|Target System Class for wormholes
# 1382|7|wormholeMaxStableTime|The maximum amount of time a wormhole will stay open
# 1383|7|wormholeMaxStableMass|The maximum amount of mass a wormhole can transit before collapsing
# 1384|7|wormholeMassRegeneration|The amount of mass a wormhole regenerates per cycle
# 1385|7|wormholeMaxJumpMass|The maximum amount of mass that can transit a wormhole in one go
# 1386|7|wormholeTargetRegion1|Specific target region 1 for wormholes
# 1387|7|wormholeTargetRegion2|Specific target region 2 for wormholes
# 1388|7|wormholeTargetRegion3|Specific target region 3 for wormholes
# 1389|7|wormholeTargetRegion4|Specific target region 4 for wormholes
# 1390|7|wormholeTargetRegion5|Specific target region 5 for wormholes
# 1391|7|wormholeTargetRegion6|Specific target region 6 for wormholes
# 1392|7|wormholeTargetRegion7|Specific target region 7 for wormholes
# 1393|7|wormholeTargetRegion8|Specific target region 8 for wormholes
# 1394|7|wormholeTargetRegion9|Specific target region 9 for wormholes
# 1395|7|wormholeTargetConstellation1|Specific target constellation 1 for wormholes
# 1396|7|wormholeTargetConstellation2|Specific target constellation 2 for wormholes
# 1397|7|wormholeTargetConstellation3|Specific target constellation 3 for wormholes
# 1398|7|wormholeTargetConstellation4|Specific target constellation 4 for wormholes
# 1399|7|wormholeTargetConstellation5|Specific target constellation 5 for wormholes
# 1400|7|wormholeTargetConstellation6|Specific target constellation 6 for wormholes
# 1401|7|wormholeTargetConstellation7|Specific target constellation 7 for wormholes
# 1402|7|wormholeTargetConstellation8|Specific target constellation 8 for wormholes
# 1403|7|wormholeTargetConstellation9|Specific target constellation 9 for wormholes
# 1404|7|wormholeTargetSystem1|Specific target system 1 for wormholes
# 1405|7|wormholeTargetSystem2|Specific target system 2 for wormholes
# 1406|7|wormholeTargetSystem3|Specific target system 3 for wormholes
# 1407|7|wormholeTargetSystem4|Specific target system 4 for wormholes
# 1408|7|wormholeTargetSystem5|Specific target system 5 for wormholes
# 1409|7|wormholeTargetSystem6|Specific target system 6 for wormholes
# 1410|7|wormholeTargetSystem7|Specific target system 7 for wormholes
# 1411|7|wormholeTargetSystem8|Specific target system 8 for wormholes
# 1412|7|wormholeTargetSystem9|Specific target system 9 for wormholes
# 1457|7|wormholeTargetDistribution|This is the distribution ID of the target wormhole distribution
# 1908|6|scanWormholeStrength|Wormhole signature strength.
# categoryID = 7 => 7|Miscellaneous|Misc. attributes
