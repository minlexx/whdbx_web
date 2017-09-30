# -*- coding: utf-8 -*-
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
