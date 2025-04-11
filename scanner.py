
import os
import json
import glob
import shutil
import sqlite3
import tempfile
from utils import CHROMIUM_BROWSERS, FIREFOX_PATH, TARGET_STRINGS, convert_chrome_time, convert_firefox_time

def query_chromium_history(db_path, browser_name, profile='Default'):
    results = []
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copy2(db_path, temp_file.name)
            conn = sqlite3.connect(temp_file.name)
            cursor = conn.cursor()
            for target in TARGET_STRINGS:
                cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls WHERE url LIKE ?", (f"%{target}%",))
                for row in cursor.fetchall():
                    results.append(f"[{browser_name}] {row[0]} | {row[1]} | Visits: {row[2]} | Last: {convert_chrome_time(row[3])}")
            conn.close()
    except Exception as e:
        results.append(f"[{browser_name}] Error scanning history: {e}")
    return results

def detect_chromium_logins(browser_name, profile_path):
    detections = []
    login_path = os.path.join(profile_path, 'Login Data')
    if os.path.exists(login_path):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                shutil.copy2(login_path, temp_file.name)
                conn = sqlite3.connect(temp_file.name)
                cursor = conn.cursor()
                for target in TARGET_STRINGS:
                    cursor.execute("SELECT origin_url FROM logins WHERE origin_url LIKE ?", (f"%{target}%",))
                    if cursor.fetchone():
                        detections.append(f"[{browser_name}] Profile: {os.path.basename(profile_path)} — Saved login for {target}")
                conn.close()
        except Exception as e:
            detections.append(f"[{browser_name}] Error scanning logins: {e}")
    return detections

def scan_deleted_history_raw(db_path, browser, profile):
    results = []
    try:
        with open(db_path, 'rb') as f:
            data = f.read().decode('latin-1', errors='ignore')
            for target in TARGET_STRINGS:
                if target in data:
                    results.append(f"[{browser} - {profile}] Possible deleted visit: {target}")
    except Exception as e:
        results.append(f"[{browser}] Error reading raw history: {e}")
    return results

def detect_chromium_browsers():
    output = []
    for browser, base_path in CHROMIUM_BROWSERS.items():
        if os.path.exists(base_path):
            profiles = glob.glob(os.path.join(base_path, "*"))
            for profile in profiles:
                if os.path.isdir(profile):
                    history_path = os.path.join(profile, 'History')
                    if os.path.exists(history_path):
                        profile_name = os.path.basename(profile)
                        output += query_chromium_history(history_path, browser, profile_name)
                        output += detect_chromium_logins(browser, profile)
                        output += scan_deleted_history_raw(history_path, browser, profile_name)
    return output

def query_firefox_history(db_path, profile_name):
    results = []
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copy2(db_path, temp_file.name)
            conn = sqlite3.connect(temp_file.name)
            cursor = conn.cursor()
            for target in TARGET_STRINGS:
                cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places WHERE url LIKE ?", (f"%{target}%",))
                for row in cursor.fetchall():
                    results.append(f"[Firefox] {row[0]} | {row[1]} | Visits: {row[2]} | Last: {convert_firefox_time(row[3])}")
            conn.close()
    except Exception as e:
        results.append(f"[Firefox] Error scanning history for {profile_name}: {e}")
    return results

def detect_firefox_logins(profile_path, profile_name):
    detections = []
    login_file = os.path.join(profile_path, 'logins.json')
    if os.path.exists(login_file):
        try:
            with open(login_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry in data.get('logins', []):
                    hostname = entry.get('hostname', '')
                    for target in TARGET_STRINGS:
                        if target in hostname:
                            detections.append(f"[Firefox] Profile: {profile_name} — Saved login for {target}")
        except Exception as e:
            detections.append(f"[Firefox] Error scanning logins for {profile_name}: {e}")
    return detections

def detect_firefox():
    output = []
    if os.path.exists(FIREFOX_PATH):
        for profile in os.listdir(FIREFOX_PATH):
            full_path = os.path.join(FIREFOX_PATH, profile)
            db_path = os.path.join(full_path, 'places.sqlite')
            if os.path.exists(db_path):
                output += query_firefox_history(db_path, profile)
                output += detect_firefox_logins(full_path, profile)
    return output

def run_full_scan():
    return detect_chromium_browsers() + detect_firefox()
