# encoding=utf-8

import urllib2,urllib
import time
import hashlib
import requests
import json

API_KEY = '1111111111111111111'
SECRET_KEY = '22222222222'



def get_headers(URL, BODY):

    # Wed, 24 Dec 2014 08:26:21 +0800
    API_REQUEST_DATE= time.strftime("%a, %d %b %Y %H:%M:%S +0800", time.localtime())
    API_FORMAT      = 'json'
    API_HMAC        = hashlib.md5(API_KEY + URL + BODY + API_REQUEST_DATE + SECRET_KEY).hexdigest()

    headers = {
        'API-KEY': API_KEY,
        'API-REQUEST-DATE': API_REQUEST_DATE,
        'API-HMAC': API_HMAC,
        'API-FORMAT': API_FORMAT,
    }

    return headers


def get_domain():

    url = 'https://www.cloudxns.net/api2/domain'
    body = ''
    req = urllib2.Request(url, headers=get_headers(url, body))
    resp = urllib2.urlopen(req)

    return resp.read()


def get_dns_entry():

    domain_id = '333333'
    url = 'https://www.cloudxns.net/api2/record/%s?host_id=0' % domain_id
    body = ''
    req = urllib2.Request(url, headers=get_headers(url, body))
    resp = urllib2.urlopen(req)
    return resp.read()


def alter_resolve(record_id, domain_id, host, value, ttl, type):

    url = 'https://www.cloudxns.net/api2/record/%s' % record_id
    body = {
        'domain_id': domain_id,
        'host': host,
        'value': value,
        'type': type,
    }

    body = json.dumps(body)

    r = requests.put(url, body, headers=get_headers(url,body))

    return r

def _default_proxy(value):

    record_id   = '5555555'
    domain_id   = 7777
    host        = 'myvpn'
    ttl         = 600
    type        = 'LINK'

    try:
        resp = alter_resolve(record_id, domain_id, host, value, ttl, type)
        resp_json = resp.json()

        if resp.status_code == 200 and resp_json['message'] == 'success':
            return True
        else:
            return False

    except Exception as e:
        print e
        return False



def _DEFAULT2NJ():
    value = 'nj.proxy@tyr.gift'
    return _default_proxy(value)

def _DEFAULT2BJ():
    value = 'bj.proxy@tyr.gift'
    return _default_proxy(value)

def _nj_proxy(value):

    record_id = ['1878281', '1878283', '1878285', '1878287']
    domain_id   = 73295
    host        = 'proxy'
    ttl         = 80
    type        = 'LINK'

    def _set(record_id, value):
        try:
            resp = alter_resolve(record_id, domain_id, host, value, ttl, type)
            resp_json = resp.json()

            if resp.status_code == 200 and resp_json['message'] == 'success':
                return True
            else:
                return False

        except Exception as e:
            print e
            return False

    flag = True
    for id in record_id:
        if not _set(id, value):
            flag = False
            sendmsg('CloudXNS set record_id: %s to bj_proxy failed!' % id)
            print 'set fail for : %s' % id

    if flag:
        print 'nj.proxy switch to bj_proxy success!'
        return True
    else:
        print 'nj.proxy switch to bj_proxy fail!'
        return False

def _NJ2NJ():
    value  = 'nj.proxy@tyr.gift'
    return _nj_proxy(value)

def _NJ2BJ():
    value = 'bj.proxy@tyr.gift'
    return _nj_proxy(value)

def bj_proxy_alive():

    url  = 'http://bj.proxy.tyr.gift:25899'
    try:
        resp = urllib2.urlopen(url)
        resp = resp.read()
        if "TyrChen's notes" in resp:
            return True
        else:
            return False
    except Exception as e:
        print e
        return False

def nj_proxy_alive():

    url  = 'http://nj.proxy.tyr.gift:25899'
    try:
        resp = urllib2.urlopen(url)
        resp = resp.read()
        if "TyrChen's notes" in resp:
            return True
        else:
            return False
    except Exception as e:
        print e
        return False

def sendmsg(msg):

    to = 'conan1993ai'
    url = 'http://xp2.im.baidu.com/ext/1.0/sendMsg'
    token = '84feb2211bebb3036c235c2ccbbd0dfc'

    data = {
        'to':           to,
        'access_token': token,
        'msg_type':     'text',
        'content':      msg
    }

    handler = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data)))
    print handler.read()




def main():

    _BJ_ON2DOWN = ''
    _NJ_ON2DOWN = ''

    INTERVEL    = 1
    retry = 10

    _of_bj = 0
    _of_nj = 0

    while True:

        ti = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if bj_proxy_alive():
            ''' cubieboard代理工作正常 '''
            print '%s bj_proxy_alive: %s' %(ti, 'ok')

            _bj_new = 'Up'
            if _BJ_ON2DOWN != _bj_new:
                sendmsg('%s bj proxy is up!' % ti)
                _BJ_ON2DOWN = _bj_new

                if _DEFAULT2BJ():
                    msg = 'Default Line Proxy Switch To BJ Success!'
                    sendmsg(msg)
                else:
                    msg = 'Default Line Proxy Switch To BJ Fail!'
                    sendmsg(msg)

        else:
            print '%s bj_proxy_alive: %s' %(ti, 'no!')
            _of_bj += 1

        if nj_proxy_alive():
            print '%s nj_proxy_alive: %s' % (ti, 'ok')
            _nj_new = 'Up'
            if _NJ_ON2DOWN != _nj_new:
                sendmsg('%s nj proxy is up!' % ti)
                _NJ_ON2DOWN = _nj_new

                if _NJ2NJ():
                    msg = 'NJ Proxy Switch To NJ Success!'
                    sendmsg(msg)
                else:
                    msg = 'NJ Proxy Switch To NJ Fail!'
                    sendmsg(msg)


        else:
            print '%s nj_proxy_alive: %s' % (ti, 'no!')
            _of_nj += 1

        if _of_bj >= retry:
            msg = '%s bj proxy is down!' % ti
            _of_bj = 0
            print msg
            _bj_new = 'Down'
            if _BJ_ON2DOWN != _bj_new:
                ''' BJ PROXY 从UP变成DOWN '''
                sendmsg(msg)
                _BJ_ON2DOWN = _bj_new
                if _DEFAULT2NJ():
                    msg = 'Default Line Proxy Switch To NJ Success!'
                    sendmsg(msg)
                else:
                    msg = 'Default Line Proxy Switch To NJ Fail!'
                    sendmsg(msg)


        elif _of_nj >= retry:
            msg = '%s nj proxy is down!' % ti
            _of_nj = 0
            print msg
            _nj_new = 'Down'
            if _NJ_ON2DOWN != _nj_new:
                sendmsg(msg)
                _NJ_ON2DOWN = _nj_new
                if _NJ2BJ():
                    msg = 'NJ Proxy Switch To BJ Success!'
                    sendmsg(msg)
                else:
                    msg = 'NJ Proxy Switch To BJ Fail!'
                    sendmsg(msg)


        time.sleep(INTERVEL)


if __name__ == '__main__':
    main()
