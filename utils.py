
import os
import datetime

TARGET_STRINGS = [
    'acdiamond.net',
    'artificialaiming.net',
    'dottyservices.online',
    'unknowncheats.me',
    'kronixsolutions.org',
    'cheatarmy.com',
    'ring-1.io'
]

CHROMIUM_BROWSERS = {
    'Chrome': os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\'),
    'Edge': os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\'),
    'Brave': os.path.expanduser('~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\'),
    'Vivaldi': os.path.expanduser('~\\AppData\\Local\\Vivaldi\\User Data\\'),
    'Opera': os.path.expanduser('~\\AppData\\Roaming\\Opera Software\\Opera Stable\\'),
}

FIREFOX_PATH = os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\')

def convert_chrome_time(chrome_time):
    if chrome_time == 0:
        return ''
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)).strftime('%Y-%m-%d %H:%M:%S')

def convert_firefox_time(moz_time):
    if moz_time == 0:
        return ''
    return datetime.datetime.fromtimestamp(moz_time / 1_000_000).strftime('%Y-%m-%d %H:%M:%S')
