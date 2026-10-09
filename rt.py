import time
import requests
import sqlite3

baseurl = 'https://collectionapi.metmuseum.org/public/collection/v1/' 
session = requests.Session()


def get_object_ids(query):
    r = session.get(f'{baseurl}/search', params={'q': query}, timeout = 10)
    r.raise_for_status()
    return r.json().get('objectIDs') or []


def get_object(object_id, retries = 3):
    for attempt in range(1, retries + 1):
        r = session.get(f'{baseurl}/objects/{object_id}', timeout = 10)
        if r.status_code == 404:

            return None
        if r.status_code in (403, 429) or r.status_code >= 500:
            time.sleep(2 * attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f'Object {object_id}: failed after {retries} attempts')

def extract(name, limit):
    ids = get_object_ids(name)[:limit]
    raw = []
    for object_id in ids:
        obj = get_object(object_id)
        if ids is not None:
            raw.append(obj)
        time.sleep(0.1)
    return raw

def transform(raw):
    rows = []
    for obj in raw:
        row = {
            "object_id": obj['objectID'],
            "title": obj["title"] or None,
            "culture": obj["culture"] or None,
            "period": obj["period"] or None,
            "object_date": obj["objectDate"] or None,
            "begin_year": obj["objectBeginDate"],
            "end_year": obj["objectEndDate"],
            "medium": obj["medium"] or None,
            "department": obj["department"] or None,
        }
        if row['title'] is None:
            continue
        rows.append(row)
    return rows
        

def load(rows, db_name='met.db'):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                object_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                culture TEXT,
                period TEXT,
                object_date TEXT,
                begin_year INTEGER,
                end_year INTEGER,
                medium TEXT,
                department TEXT
                )
    """)
    cur.executemany("""
        INSERT OR REPLACE INTO objects
                    VALUES (
                    :object_id, :title, :culture, :period, :object_date, :begin_year, 
                    :end_year, :medium, :department)
                    """, rows)
    
    conn.commit()
    conn.close()



load(transform(extract('Athena', 30)))
        