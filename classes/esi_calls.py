# -*- coding: utf-8 -*-
import datetime
import json
import os
import os.path

import requests

from . import sitecfg


esi_proxies = None


def set_esi_proxies(proxies: dict):
    global esi_proxies
    esi_proxies = proxies


class ESIException(Exception):
    def __init__(self, msg: str = ''):
        self.msg = msg

    def error_string(self) -> str:
        return self.msg


def analyze_esi_response_headers(headers: dict) -> None:
    """
    Keep track of ESI headers: watch for deprecated endpoints
    and error rate limiting
    :param headers: requests's resonse headers dict
    :return:
    """
    lines_to_log = []
    dt_now_str = str(datetime.datetime.utcnow()) + ' UTC: '  # '2018-03-09 11:16:11.178443 UTC: '
    if 'warning' in headers:
        lines_to_log.append(dt_now_str + 'warning header: {}'.format(headers['warning']))
    if 'X-ESI-Error-Limit-Remain' in headers:
        errors_remain = int(headers['X-ESI-Error-Limit-Remain'])
        if errors_remain < 50:
            lines_to_log.append(dt_now_str + 'X-ESI-Error-Limit-Remain < {} !!!\n'.format(errors_remain))
    if len(lines_to_log) < 1:
        return
    try:
        # auto-create logs subdir
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        fn = './logs/esi-warnings.log'
        with open(fn, mode='at', encoding='utf-8') as f:
            f.writelines(lines_to_log)
    except IOError:
        pass


def universe_names(cfg: sitecfg.SiteConfig, ids_list: list) -> list:
    global esi_proxies
    ret = []
    error_str = ''
    if len(ids_list) <= 0:
        return ret
    try:
        # https://esi.evetech.net/ui/?version=latest#/Universe/post_universe_names
        url = '{}/universe/names/'.format(cfg.ESI_BASE_URL)
        ids_str = '['
        for an_id in set(ids_list):
            if len(ids_str) > 1:
                ids_str += ','
            ids_str += str(an_id)
        ids_str += ']'
        r = requests.post(url,
                          headers={
                              'Content-Type': 'application/json',
                              'Accept': 'application/json',
                              'User-Agent': cfg.SSO_USER_AGENT
                          },
                          data=ids_str,
                          proxies=esi_proxies,
                          timeout=20)
        response_text = r.text
        if r.status_code == 200:
            ret = json.loads(response_text)
            analyze_esi_response_headers(r.headers)
        else:
            obj = json.loads(response_text)
            if 'error' in obj:
                error_str = 'ESI error: {}'.format(obj['error'])
            else:
                error_str = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        error_str = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        error_str = 'Failed to parse response JSON from CCP ESI server!'
    if error_str != '':
        raise ESIException(error_str)
    # ret == [{'category': 'character', 'name': 'Xur Hermit', 'id': 2114246032}]
    return ret


def public_data(cfg: sitecfg.SiteConfig, char_id: int) -> dict:
    global esi_proxies
    ret = {
        'error': '',
        'char_id': char_id,
        'char_name': '',
        'corp_id': 0,
        'corp_name': '',
        'corp_ticker': '',
        'corp_member_count': 0,
        'ally_id': 0
    }
    try:
        # We need to send 2 requests, first get corpiration_id from character info,
        #   next - get corporation name by corporation_id. Both of these calls do
        #   not require authentication in ESI scopes.

        # 1. first request for character public details
        # https://esi.tech.ccp.is/latest/#!/Character/get_characters_character_id
        # This route is cached for up to 3600 seconds
        url = '{}/characters/{}/'.format(cfg.ESI_BASE_URL, char_id)
        r = requests.get(url,
                         headers={
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['char_name'] = details['name']
            ret['corp_id'] = details['corporation_id']
            analyze_esi_response_headers(r.headers)
        else:
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)

        # 2. second request for corporation public details
        # https://esi.tech.ccp.is/latest/#!/Corporation/get_corporations_corporation_id
        # This route is cached for up to 3600 seconds
        url = '{}/corporations/{}/'.format(cfg.ESI_BASE_URL, ret['corp_id'])
        r = requests.get(url,
                         headers={
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['corp_name'] = str(details['name'])
            ret['corp_ticker'] = str(details['ticker'])
            ret['corp_member_count'] = str(details['member_count'])
            if 'alliance_id' in details:  # it may be not present
                ret['ally_id'] = str(details['alliance_id'])
            analyze_esi_response_headers(r.headers)
        else:
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        ret['error'] = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        ret['error'] = 'Failed to parse response JSON from CCP ESI server!'
    return ret


def do_refresh_token(cfg: sitecfg.SiteConfig, refresh_token: str) -> dict:
    res = {
        'error': '',
        'sso_expire_dt_utc': '',
        'del': {
            'sso_token': '',
            'sso_refresh_token': '',
            'sso_expire_dt': '',
            'sso_expire_dt_utc': ''
        }
    }
    try:
        r = requests.post('https://login.eveonline.com/oauth/token',
                          auth=(cfg.SSO_CLIENT_ID, cfg.SSO_SECRET_KEY),
                          headers={
                              'Content-Type': 'application/x-www-form-urlencoded',
                              'User-Agent': cfg.SSO_USER_AGENT
                          },
                          data={
                              'grant_type': 'refresh_token',
                              'refresh_token': refresh_token
                          },
                          timeout=10)
        if (r.status_code >= 200) and (r.status_code < 300):
            response_text = r.text
            details = json.loads(response_text)
            # calculate expire datetime
            expires_in = int(details['expires_in'])
            td = datetime.timedelta(seconds=expires_in)
            dt_now = datetime.datetime.now()
            dt_utcnow = datetime.datetime.utcnow()
            dt_expire = dt_now + td
            dt_utcexpire = dt_utcnow + td
            # form reply dict
            res['sso_expire_dt_utc'] = dt_utcexpire.strftime('%Y-%m-%dT%H:%M:%SZ')
            res['del']['sso_token'] = details['access_token']
            res['del']['sso_refresh_token'] = details['refresh_token']
            res['del']['sso_expire_dt'] = dt_expire
            res['del']['sso_expire_dt_utc'] = dt_utcexpire
        else:
            # some SSO error
            res['error'] = 'Error during communication to login.eveonline.com ' \
                           '(refresh token), HTTP error={}'.format(r.status_code)
    except requests.exceptions.RequestException as req_e:
        res['error'] = 'Error during communication to login.eveonline.com ' \
                       '(refresh token): ' + str(req_e)
    except json.JSONDecodeError as json_e:
        res['error'] = 'Error decoding server response from ' \
                       'login.eveonline.com! (refresh token)' + str(json_e)
    return res


def location_online(cfg: sitecfg.SiteConfig, char_id: int, access_token: str) -> dict:
    global esi_proxies
    ret = {
        'error': '',
        'is_online': False
    }
    try:
        # https://esi.tech.ccp.is/latest/#!/Location/get_characters_character_id_online
        # This route is cached for up to 60 seconds
        url = '{}/characters/{}/online/'.format(cfg.ESI_BASE_URL, char_id)
        r = requests.get(url,
                         headers={
                             'Authorization': 'Bearer ' + access_token,
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=10)
        response_text = r.text
        # '{"last_login":"2018-05-22T22:52:32Z","last_logout":"2018-05-19T20:43:44Z","logins":505,"online":true}'
        if r.status_code == 200:
            obj = json.loads(r.text)
            ret['is_online'] = obj['online']
            ret['online'] = obj['online']
            ret['logins'] = obj['logins']
            ret['error'] = ''
            analyze_esi_response_headers(r.headers)
        else:
            obj = json.loads(r.text)
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        ret['error'] = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        ret['error'] = 'Failed to parse response JSON from CCP ESI server!'
    return ret


def location_ship(cfg: sitecfg.SiteConfig, char_id: int, access_token: str) -> dict:
    global esi_proxies
    ret = {
        'error': '',
        'ship_name': '',
        'ship_type_id': 0
    }
    try:
        # https://esi.tech.ccp.is/latest/#!/Location/get_characters_character_id_ship
        # This route is cached for up to 5 seconds
        url = '{}/characters/{}/ship/'.format(cfg.ESI_BASE_URL, char_id)
        r = requests.get(url,
                         headers={
                             'Authorization': 'Bearer ' + access_token,
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['ship_name'] = str(details['ship_name'])
            ret['ship_type_id'] = int(details['ship_type_id'])
            analyze_esi_response_headers(r.headers)
        else:
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        ret['error'] = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        ret['error'] = 'Failed to parse response JSON from CCP ESI server!'
    return ret


def location_location(cfg: sitecfg.SiteConfig, char_id: int, access_token: str) -> dict:
    global esi_proxies
    ret = {
        'error': '',
        'solarsystem_id': 0,
        'solarsystem_name': '',
        'is_whsystem': False,
        'is_docked': False,
        'structure_id': 0,
        'station_id': 0
    }
    try:
        # https://esi.tech.ccp.is/latest/#!/Location/get_characters_character_id_location
        # Information about the characters current location. Returns the current solar system id,
        # #    and also the current station or structure ID if applicable.
        # This route is cached for up to 5 seconds
        url = '{}/characters/{}/location/'.format(cfg.ESI_BASE_URL, char_id)
        r = requests.get(url,
                         headers={
                             'Authorization': 'Bearer ' + access_token,
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['solarsystem_id'] = int(details['solar_system_id'])
            if 'structure_id' in details:
                ret['is_docked'] = True
                ret['structure_id'] = details['structure_id']
            if 'station_id' in details:
                ret['is_docked'] = True
                ret['station_id'] = details['station_id']
            analyze_esi_response_headers(r.headers)
        else:
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        ret['error'] = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        ret['error'] = 'Failed to parse response JSON from CCP ESI server!'
    return ret


def market_region_orders(cfg: sitecfg.SiteConfig, region_id: int, order_type: str, optional_type_id: int = None) -> list:
    global esi_proxies
    ret = []
    error_str = ''
    if region_id < 0:
        return ret
    if order_type not in ['buy', 'sell', 'all']:
        raise ValueError('order_type must be one of: "buy", "sell", "all"')
    try:
        # https://esi.tech.ccp.is/latest/#!/Market/get_markets_region_id_orders
        # This route is cached for up to 300 seconds
        # example request URL: https://esi.tech.ccp.is/latest/markets/10000002/orders/?order_type=sell&type_id=30377
        url = '{}/markets/{}/orders/'.format(cfg.ESI_BASE_URL, region_id)
        get_params = {
            'order_type': order_type
        }
        if optional_type_id is not None:
            get_params['type_id'] = optional_type_id
        r = requests.get(url,
                         params=get_params,
                         headers={
                             'Content-Type': 'application/json',
                             'Accept': 'application/json',
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         proxies=esi_proxies,
                         timeout=20)
        response_text = r.text
        if r.status_code == 200:
            ret = json.loads(response_text)
            analyze_esi_response_headers(r.headers)
        else:
            obj = json.loads(response_text)
            if 'error' in obj:
                error_str = 'ESI error: {}'.format(obj['error'])
            else:
                error_str = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        error_str = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        error_str = 'Failed to parse response JSON from CCP ESI server!'
    if error_str != '':
        raise ESIException(error_str)
    return ret


def ui_open_window_information(cfg: sitecfg.SiteConfig, target_id: int, access_token: str) -> bool:
    """
    Open the information window for a character, corporation or alliance inside the client
    :param cfg: configuration
    :param target_id: can be character_id, corporation_id, alliance_id
    :param access_token: SSO access token string
    :return: true - request received, on error ESIExceprtion is thrown
    """
    global esi_proxies
    ret = False
    error_str = ''
    if target_id < 0:
        return False
    try:
        # https://esi.tech.ccp.is/latest/#!/User32Interface/post_ui_openwindow_information
        url = '{}/ui/openwindow/information/'.format(cfg.ESI_BASE_URL)
        r = requests.post(url,
                          params={'target_id': target_id},
                          headers={
                              'Authorization': 'Bearer ' + access_token,
                              'Content-Type': 'application/json',
                              'Accept': 'application/json',
                              'User-Agent': cfg.SSO_USER_AGENT
                          },
                          proxies=esi_proxies,
                          timeout=10)
        # only check return code. 204 is "reqeust accepted"
        if (r.status_code >= 200) and (r.status_code <= 299):
            ret = True
            analyze_esi_response_headers(r.headers)
        else:
            error_str = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)
    except requests.exceptions.RequestException as e:
        error_str = 'Error connection to ESI server: {}'.format(str(e))
    except json.JSONDecodeError:
        error_str = 'Failed to parse response JSON from CCP ESI server!'
    if error_str != '':
        raise ESIException(error_str)
    return ret
