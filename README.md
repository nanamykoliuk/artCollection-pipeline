# Art Collection Pipeline

A small ETL pipeline in Python. It searches the Metropolitan Museum of Art
Collection API for a keyword, fetches the matching objects, and stores them
in a local SQLite database.

## What it does

1. Extract: searches the Met API (v1.1) for a keyword and fetches the details of each matching object. Missing objects (404) are skipped, and temporary errors (403, 429, 5xx) are retried with a growing delay.
2. Transform: keeps the fields I need (title, culture, period, date, begin and end year, medium, department), turns empty strings into NULL, and drops objects without a title.
3. Load: writes the rows into the SQLite file met.db. object_id is the primary key and the insert uses INSERT OR REPLACE, so running the script again updates existing rows instead of creating duplicates.

## How to run

    pip install -r requirements.txt
    python rt.py

The database met.db is created next to rt.py. The keyword and the number of
results are set in the last line of the script:

    load(transform(extract('Athena', 30)))

## Example query

    sqlite3 met.db "SELECT title, culture, object_date FROM objects LIMIT 5;"

## Tech

Python, requests, sqlite3

## Ideas for improvement

1. Take the keyword and limit as command line arguments
2. Run several search terms in one go (for example Zeus, Apollo, Hera)
3. Add tests for the transform step
4. Log progress instead of staying silent while fetching
