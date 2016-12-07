from gevent import monkey
monkey.patch_all()
import gevent.pywsgi
import logging as log
from flask import Flask, request, make_response
import certifi
import urllib3
from werkzeug.contrib.cache import SimpleCache
import os
import sys
import time
import datetime
import json
import re
import sitemap.generator as smg
from pprint import pformat as pf
# from pprint import pprint as pp


log_level = str(os.getenv('LOG_LEVEL', 'INFO')).upper()
json_url = str(
    os.getenv(
        'JSON_URL',
        'https://www.example.com/api/xxx/v3/products?size=1000&cnty={0}'))
base_url = str(os.getenv('BASE_URL', 'https://www.example.com'))
apps_path = str(os.getenv('APPS_PATH', '/apps/{0}'))
apps_change_frequency = str(os.getenv('APPS_CHANGE_FREQUENCY', 'weekly'))
apps_priority = str(os.getenv('APPS_PRIORITY', '0.5'))
add_paths = str(
    os.getenv(
        'ADD_PATHS',
        "{0}/,daily,1.0\n{0}/list/desktop,weekly,0.8\n{0}/termofuse,monthly,0.2"))
cache_time = str(os.getenv('CACHE_TIME', '3600'))

log.getLogger('').setLevel(log.getLevelName(log_level))
log.debug('LOG_LEVEL: ' + str(log_level))
log.debug('JSON_URL: ' + str(json_url))
log.debug('BASE_URL: ' + str(base_url))
log.debug('APPS_PATH: ' + str(apps_path))
log.debug('APPS_CHANGE_FREQUENCY: ' + str(apps_change_frequency))
log.debug('APPS_PRIORITY: ' + str(apps_priority))
log.debug('ADD_PATHS: ' + str(add_paths))
log.debug('CACHE_TIME: ' + str(cache_time))

if '{0}' not in apps_path:
    log.error(
        '**** ATTENTION! WARNING ERROR: Your APPS_PATH does not contain a "{0}" placeholder for each app_id. You should check your APPS_PATH is correct ****')
    time.sleep(2)
    sys.exit(1)

flask_app = Flask(__name__)
cache = SimpleCache()

log.getLogger('werkzeug').setLevel(log.getLevelName(log_level))
log.getLogger('urllib3').setLevel(log.getLevelName(log_level))


def this_version_string():
    si = sys.implementation
    sv = sys.version_info
    return json.dumps({ "python": """{0}-{1}.{2}.{3}-{4}-{5}""".format(si.name,
                                                                       sv.major,
                                                                       sv.minor,
                                                                       sv.micro,
                                                                       sv.releaselevel,
                                                                       sv.serial).lower(),
                        "config": str(os.getenv('APP_CONFIG_VERSION',
                                                'unknown'))},
                      indent=4,
                      sort_keys=True)


def get_url_data(url, cc):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()
    )
    try:
        r = http.request(
            'GET',
            url.format(
                cc.upper()),
            retries=urllib3.Retry(
                total=4,
                connect=2.0,
                read=6.0,
                redirect=0,
                raise_on_status=True,
                raise_on_redirect=True,
                status_forcelist=[
                    500,
                    501,
                    502,
                    503,
                    504,
                    400,
                    401,
                    403,
                    404]))
        response = r.data.decode('utf-8')
    except urllib3.exceptions.HTTPError as e:
        log.error("Error getting: %r\n%r" % (json_url, e))
        response = """"""
    return response


def find_country_app_id(s, cc):
    lst = []
    if not s:
        return lst
    try:
        j = json.loads(s)
        for content in j['contents']:
            log.debug('app_ids: ' + pf(content['app_ids']))
            log.debug('countries: ' + pf(content['countries']))
            # if cc not in content['countries']:
            #    continue
            for app_id in content['app_ids']:
                if app_id not in lst:
                    lst.append(app_id)
    except (json.JSONDecodeError, KeyError) as e:
        log.warning("JSON Error: %r" % e)
        pass
    return lst


def sm_from_app_id(lst, cc):
    sm = smg.Sitemap()
    for add_path in add_paths.split("\n"):
        a_path, c_freq, a_priority = add_path.split(',')
        sm.add(a_path.format(base_url), changefreq=c_freq, priority=a_priority)
    for app_id in lst:
        sm.add(
            base_url +
            apps_path.format(app_id),
            changefreq=apps_change_frequency,
            priority=apps_priority)
    return sm.generate() + """<!-- Where: {0}, When: {1}, App_Count: {2} -->""".format(
        cc.upper(), str(datetime.datetime.now()), str(len(lst)))


@flask_app.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    cc = request.headers.get('X-Request-Country-Code')
    if re.fullmatch( r"""^[A-Z]{2}$""", str(cc)):
        cc = str(cc).lower()
    else:
        cc = 'us'

    log.debug('cc: ' + cc)

    rv = cache.get('smxml_' + cc)
    if rv is None:
        app_lst = find_country_app_id(get_url_data(json_url, cc), cc)
        rv = sm_from_app_id(app_lst, cc)
        cache.set('smxml_' + cc, rv, timeout=int(cache_time))

    response = make_response(rv)
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Cache-Control'] = 'public, max-age=' + cache_time
    response.headers['X-Request-Country-Code'] = cc.upper()
    response.headers['X-Served-Time'] = str(datetime.datetime.now())
    response.headers['Server'] = 'SiteMap'
    return response


@flask_app.route('/version', methods=['GET'])
def version():
    response = make_response(this_version_string())
    response.headers['Server'] = 'SiteMap'
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    gevent_server = gevent.pywsgi.WSGIServer(('', 8888), flask_app, log=None)
    gevent_server.serve_forever()  # instead of flask_app.run()
