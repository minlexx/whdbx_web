# -*- coding: utf-8 -*-
import datetime
import json

import requests

from . import sitecfg


class ESIException(Exception):
    def __init__(self, msg: str = ''):
        self.msg = msg

    def error_string(self) -> str:
        return self.msg


def characters_names(cfg: sitecfg.SiteConfig, ids_list: list) -> list:
    ret = []
    error_str = ''
    if len(ids_list) < 0: return ret
    try:
        # https://esi.tech.ccp.is/latest/#!/Character/get_characters_names
        # This route is cached for up to 3600 seconds
        url = '{}/characters/names/'.format(cfg.ESI_BASE_URL)
        ids_str = ''
        for an_id in set(ids_list):
            if len(ids_str) > 0: ids_str += ','
            ids_str += str(an_id)
        r = requests.get(url,
                         params={'character_ids': ids_str},
                         headers={'User-Agent': cfg.SSO_USER_AGENT},
                         timeout=20)
        response_text = r.text
        if r.status_code == 200:
            ret = json.loads(response_text)
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


def corporations_names(cfg: sitecfg.SiteConfig, ids_list: list) -> list:
    ret = []
    error_str = ''
    if len(ids_list) < 0: return ret
    try:
        # https://esi.tech.ccp.is/latest/#!/Corporation/get_corporations_names
        # This route is cached for up to 3600 seconds
        url = '{}/corporations/names/'.format(cfg.ESI_BASE_URL)
        ids_str = ''
        for an_id in set(ids_list):
            if len(ids_str) > 0: ids_str += ','
            ids_str += str(an_id)
        r = requests.get(url,
                         params={'corporation_ids': ids_str},
                         headers={'User-Agent': cfg.SSO_USER_AGENT},
                         timeout=20)
        response_text = r.text
        if r.status_code == 200:
            ret = json.loads(response_text)
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


def alliances_names(cfg: sitecfg.SiteConfig, ids_list: list) -> list:
    ret = []
    error_str = ''
    if len(ids_list) < 0: return ret
    try:
        # https://esi.tech.ccp.is/latest/#!/Alliance/get_alliances_names
        # This route is cached for up to 3600 seconds
        url = '{}/alliances/names/'.format(cfg.ESI_BASE_URL)
        ids_str = ''
        for an_id in set(ids_list):
            if len(ids_str) > 0: ids_str += ','
            ids_str += str(an_id)
        r = requests.get(url,
                         params={'alliance_ids': ids_str},
                         headers={'User-Agent': cfg.SSO_USER_AGENT},
                         timeout=20)
        response_text = r.text
        if r.status_code == 200:
            ret = json.loads(response_text)
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


def public_data(cfg: sitecfg.SiteConfig, char_id: int) -> dict:
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
        r = requests.get(url, headers={'User-Agent': cfg.SSO_USER_AGENT}, timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['char_name'] = details['name']
            ret['corp_id'] = details['corporation_id']
        else:
            if 'error' in obj:
                ret['error'] = 'ESI error: {}'.format(obj['error'])
            else:
                ret['error'] = 'Error connecting to ESI server: HTTP status {}'.format(r.status_code)

        # 2. second request for corporation public details
        # https://esi.tech.ccp.is/latest/#!/Corporation/get_corporations_corporation_id
        # This route is cached for up to 3600 seconds
        url = '{}/corporations/{}/'.format(cfg.ESI_BASE_URL, ret['corp_id'])
        r = requests.get(url, headers={'User-Agent': cfg.SSO_USER_AGENT}, timeout=10)
        obj = json.loads(r.text)
        if r.status_code == 200:
            details = json.loads(r.text)
            ret['corp_name'] = str(details['corporation_name'])
            ret['corp_ticker'] = str(details['ticker'])
            ret['corp_member_count'] = str(details['member_count'])
            if 'alliance_id' in details:  # it may be not present
                ret['ally_id'] = str(details['alliance_id'])
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
            'sso_expire_dt': ''
        }
    }
    try:
        r = requests.post('https://login.eveonline.com/oauth/token',
                          auth = (cfg.SSO_CLIENT_ID, cfg.SSO_SECRET_KEY),
                          headers = {
                              'Content-Type': 'application/x-www-form-urlencoded',
                              'User-Agent': cfg.SSO_USER_AGENT
                          },
                          data = {
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
            res['del']['sso_token'] = details['access_token']
            res['del']['sso_refresh_token'] = details['refresh_token']
            res['del']['sso_expire_dt'] = dt_expire
            res['sso_expire_dt_utc'] = dt_utcexpire.strftime('%Y-%m-%dT%H:%M:%SZ')
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
    ret = {
        'error': '',
        'is_online': False
    }
    try:
        # https://esi.tech.ccp.is/latest/#!/Location/get_characters_character_id_online
        # This route is cached for up to 60 seconds
        url = '{}/characters/{}/online/'.format(cfg.ESI_BASE_URL, char_id)
        r = requests.get(url,
                         headers = {
                             'Authorization': 'Bearer ' + access_token,
                             'User-Agent': cfg.SSO_USER_AGENT
                         },
                         timeout = 10)
        response_text = r.text
        if r.status_code == 200:
            if str(response_text).lower() == 'true':
                ret['is_online'] = True
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
