# -*- coding: utf-8 -*-

from .database import SiteDb, WHClass, get_ss_security_color


class WHStatic:
    def __init__(self, name):
        self.name = name
        self.in_class = 0
        self.in_class_str = ''
        self.max_jump_mass = 0
        self.max_jump_mass_tt = 0
        self.max_mass = 0
        self.max_mass_tt = 0
        self.lifetime_hr = 0
        self.mass_regen = 0
        if self.name is None:
            self.name = 'None'  # hot fix :)

    def load_info(self, db: SiteDb):
        row = db.query_hole_info(self.name)
        if row:
            self.in_class = int(row[0])
            self.lifetime_hr = row[1] // 60
            self.max_mass = row[2]
            self.max_mass_tt = row[2] // 1000000
            self.max_jump_mass = row[3]
            self.max_jump_mass_tt = row[3] // 1000000
            self.mass_regen = row[4]
        if self.in_class != 0:
            if self.in_class == WHClass.HISEC_WH_CLASS:
                self.in_class_str = 'High-sec'
            if self.in_class == WHClass.LOW_WH_CLASS:
                self.in_class_str = 'Low-sec'
            if self.in_class == WHClass.NULL_WH_CLASS:
                self.in_class_str = 'Null-sec'
            if (self.in_class >= 1) and (self.in_class <= 6):
                self.in_class_str = 'C' + str(self.in_class)
            if (self.in_class >= -6) and (self.in_class <= -1):
                self.in_class_str = 'C' + str(self.in_class) + ' shattered'
            if self.in_class == WHClass.THERA_WH_CLASS:
                self.in_class_str = 'Thera'
            if self.in_class == WHClass.FRIG_WH_CLASS:
                self.in_class_str = 'frig shattered'
            if WHClass.is_drifters(self.in_class):
                self.in_class_str = 'drifters'

    def is_valid(self):
        if (self.name is None) or (self.name == ''):
            return False
        if self.in_class == 0:
            return False
        if self.max_jump_mass <= 0:
            return False
        return True

    def __str__(self):
        return self.name + ' (c' + str(self.in_class) + ')'


class WHEffect:
    def __init__(self, ename: str, eclass: int):
        self.name = ename
        self.hole_class = int(eclass)
        self.hole_class_str = eclass
        self.effect_icon = ''
        self.effects = list()
        self.effect_id = 0
        if self.name is not None:
            self.effect_id = self._getid(self.name)
            self.effect_icon = self.name.lower() + '.png'
        # fix hole class str
        if self.hole_class < 0:
            self.hole_class_str = str((-1) * self.hole_class) + ' shattered'
        if self.hole_class == WHClass.FRIG_WH_CLASS:
            self.hole_class_str = 'frig shattered, class 1-3, effect class 6'
        if WHClass.is_drifters(self.hole_class):
            self.hole_class_str = 'drifters wh, effect class 2'
        # about frig holes:
        # http://community.eveonline.com/news/dev-blogs/thera-and-the-shattered-wormholes/
        # These systems will all receive anomaly and signature sites appropriate for wormholes
        # between class 1 and class 3, but will receive the system effects normally reserved for
        # C6 Wolf Rayet systems (+100% armor hit points +200% small weapon damage, -50% shield
        # resists, -50% signature size)

    def load_info(self, db: SiteDb):
        qhc = self.hole_class
        if qhc < 0:  # shattered classes
            qhc *= (-1)  # make class positive number, not negative
        # fix frig holes
        if qhc == WHClass.FRIG_WH_CLASS:
            qhc = 6  # frig holes are class 1-3 but have W-R effect class 6
        # fix for fdrifters wh:
        if WHClass.is_drifters(self.hole_class):
            qhc = 2  # drifters whs have effects from class 2
        self.effects = db.query_effect_info(self.effect_id, qhc)

    def _getid(self, ename: str):
        n = ename.lower()
        ret = 0
        if n == 'black hole':
            ret = 1
        elif n == 'magnetar':
            ret = 2
        elif n == 'red giant':
            ret = 3
        elif n == 'pulsar':
            ret = 4
        elif n == 'wolf rayet':
            ret = 5
        elif n == 'wolf-rayet star':
            ret = 5
        elif n == 'cataclysmic variable':
            ret = 6
        return ret

    def __str__(self):
        return self.name + ' class ' + str(self.hole_class)


class WHSystemPlanet:
    type_colors = {
        'barren': '#C0C0C0',
        'gas': '#FFFF00',
        'ice': '#00FFFF',
        'oceanic': '#0099FF',
        'storm': '#8C8C8C',
        'temperate': '#08B050',
        'lava': '#FF6666',
        'plasma': 'magenta',
    }

    def __init__(self):
        self.name = ''
        self.name_nbsp = ''
        self.type = ''
        self.color = '#FFFFFF'  # white

    def set_name(self, n: str):
        self.name = n
        self.name_nbsp = n.replace(' ', '&nbsp;')

    def set_type_from_string(self, s: str):
        """
        Sets planet type from 'Planet (TYPE)' to 'TYPE'
        :param s: string in form of 'Planet (TYPE)'
        :return: None
        """
        s = s.lower()
        if (s.find(' (') > 0) and (s.find(')') > 0):
            self.type = s[s.find(' (') + 2:-1]

        if self.type in WHSystemPlanet.type_colors:
            self.color = WHSystemPlanet.type_colors[self.type]


class WHSystem:
    def __init__(self, db: SiteDb):
        # DB stuff
        self._db = db
        # data
        self.is_wh = False
        self.ssys_id = 0
        self.name = ''        # J170122
        self.number_name = ''  # 170122
        self.wh_class = 0  # [-6..-1]-shat., [1..6]-normal, 7-hisec, 8-low, 9-null, 12-Thera, 13-frig, 14-18 drifters
        self.wh_star = ''
        self.wh_planets = 0
        self.wh_moons = 0
        self.wh_effect = None
        self.wh_effect_name = ''
        self.wh_statics = []
        self.wh_statics_str = ''
        self.wh_is_shattered = False
        self.reg_name = ''
        self.reg_id = 0
        self.const_name = ''
        self.const_id = 0
        self.radius = 0
        self.security = ''
        self.security_full = 0.0
        self.sec_color = '#FFFFFF'
        self.radus = 0.0
        self.radius_ae = 0.0
        self.planets = []
        # routes
        self.route_jita = None
        self.route_amarr = None
        self.route_dodixie = None
        self.route_hek = None
        self.route_rens = None
        # Hubs systems IDs
        self.JITA_ID = 30000142
        self.AMARR_ID = 30002187
        self.DODIXIE_ID = 30002659
        self.HEK_ID = 30002053
        self.RENS_ID = 30002510
        self.THERA_SSID = 31000005

    def is_valid(self):
        if (self.name != '') and (self.ssys_id != 0):
            return True
        return False

    def is_shattered(self):
        if (self.wh_class <= -1) and (self.wh_class >= -6):
            return True
        return False

    def is_frig_shattered(self):
        if self.wh_class == WHClass.FRIG_WH_CLASS:
            return True
        return False

    def is_thera(self):
        if self.ssys_id == self.THERA_SSID:
            return True
        # class 12
        if self.wh_class == WHClass.THERA_WH_CLASS:
            return True
        return False

    def is_drifters(self):
        # class 14-18
        return WHClass.is_drifters(self.wh_class)

    def __str__(self):
        s = '<System>'
        if (self.ssys_id > 0) and (self.name != ''):
            s = '<' + self.name
            if self.is_wh:
                if self.is_thera():
                    s += ', shattered'
                elif self.is_frig_shattered():
                    s += ', frig shattered'
                elif self.is_shattered():
                    s += ', class ' + str(self.wh_class * (-1)) + ' shattered'
                elif self.is_drifters():
                    s += ', drifters WH'
                else:
                    s += ', class ' + str(self.wh_class)
            else:
                s += ', ' + str(self.security)
            s += '>'
        return s

    def query_info(self, ssys_id: int):
        row = self._db.query_wormholesystem_new(ssys_id)
        # for (sclass, sstar, splanets, smoons, seffect, sstatics) in cursor: # new
        if row:
            self.is_wh = True
            self.wh_class = int(row[0])
            self.wh_star = row[1]
            self.wh_planets = int(row[2])
            self.wh_moons = int(row[3])
            self.wh_effect_name = row[4]
            self.wh_statics_str = row[5]
            if self.wh_statics_str is None:
                self.wh_statics_str = ''
            for static_name in self.wh_statics_str.split(','):
                if static_name != '':
                    st1 = WHStatic(static_name)
                    self.wh_statics.append(st1)
            if self.wh_effect_name is not None:
                self.wh_effect = WHEffect(self.wh_effect_name, self.wh_class)
            else:
                self.wh_effect = None
        if self.is_wh:
            # load extra info about static holes
            for a_static in self.wh_statics:
                a_static.load_info(self._db)
            # load info about effect
            if self.wh_effect is not None:
                self.wh_effect.load_info(self._db)
        # get additional info about it from CCP data dump
        row = self._db.query_solarsystem(ssys_id)
        # for(sname, ssec, sradius, sreg_id, sconst_id, sreg_name, sconst_name) in cursor:
        if row:
            ssec = float(row[1])
            sradius = float(row[2])
            self.name = row[0]
            if len(self.name) > 1:
                self.number_name = self.name[1:]
            self.ssys_id = ssys_id
            self.security = str(round(ssec*10) / 10.0)  # 0.830615 => '0.8'
            self.security_full = ssec
            self.sec_color = get_ss_security_color(self.security_full)
            self.radius = sradius  # 1 AE = 149597870 km
            self.radius_ae = round(sradius / 149597870000.0 * 10.0) / 10.0
            self.reg_id = int(row[3])
            self.const_id = int(row[4])
            self.reg_name = row[5]
            self.const_name = row[6]
        # get extended planets info
        self.planets = []
        pls = self._db.query_solarsystem_planets(self.ssys_id)
        for pl in pls:
            planet = WHSystemPlanet()
            planet.set_name(pl[0])
            planet.set_type_from_string(pl[1])
            self.planets.append(planet)

#
#   With Eve-Central dead, we have no easy way to get trade routes,
#        so this all is commented for a while
#
#    def query_trade_routes(self, config: sitecfg.SiteConfig):
#        # find routes to popular trade hubs:
#        if not self.is_wh:
#            ec = eve_central.EveCentral(config)
#            self.route_jita = ec.route(self.name, 'Jita')
#            self.route_amarr = ec.route(self.name, 'Amarr')
#            self.route_dodixie = ec.route(self.name, 'Dodixie')
#            self.route_hek = ec.route(self.name, 'Hek')
#            self.route_rens = ec.route(self.name, 'Rens')
#            # process
#            self.process_route_sec_colors(self.route_jita)
#            self.process_route_sec_colors(self.route_amarr)
#            self.process_route_sec_colors(self.route_dodixie)
#            self.process_route_sec_colors(self.route_hek)
#            self.process_route_sec_colors(self.route_rens)
#
#    def process_route_sec_colors(self, route):
#        if not isinstance(route, list):
#            return
#        if len(route) < 1:
#            return
#        for jump in route:
#            sec = float(jump['to']['security'])
#            jump['to']['sec_color'] = get_ss_security_color(sec)
#            sec = float(jump['from']['security'])
#            jump['from']['sec_color'] = get_ss_security_color(sec)
