#!/usr/bin/env python3

'''
    Scan a music library
'''

from argparse import ArgumentParser
import base64, curio, json, multiprocessing, os, re, sqlite3, subprocess


DBPATH = 'db.sqlite3'
AUDIO = set( ('.aac', '.flac', '.m4a', '.mp3', '.wav'))

INSERT_SQL = "INSERT INTO fingerprint (path, fp, duration) VALUES (?, ?, ?);"
SELECT_SQL = "SELECT path FROM fingerprint;"
DELETE_SQL = "DELETE FROM fingerprint WHERE path=?;"

PATHS = set()


def utf8( s):
    return s.encode('utf-8', 'surrogateescape').decode('utf-8', 'ignore')


def walk( dirs):
    'List all audio files from a list of directories'
    for path in dirs:
        if os.path.isdir( path):
            for dirpath, dirnames, filenames in os.walk( path):
                for name in filenames:
                    root, ext = os.path.splitext( name)
                    if ext.lower() in AUDIO: 
                        yield utf8( os.path.join( dirpath, name))
        else:
            root, ext = os.path.splitext( path)
            if ext.lower() in AUDIO: 
                yield utf8( path)


def fingerprint( path):
    'Get an AcoustID audio fingerprint'
    data = subprocess.run( ['fpcalc', '-json', path],
        capture_output=True, check=True, text=True, encoding='UTF8').stdout
        
    result = json.loads( data)
    fp = base64.b85decode( result['fingerprint'])
    duration = result['duration']
    
    print( path, duration)
    return (path, fp, duration)


def scan( cur, dirs):
    'Synchronize the fingerprint database with the file system'
    
    # Fetch already processed paths
    cur.execute( SELECT_SQL)
    PATHS.update( row[0] for row in cur.fetchall())
    
    # Remove vanished paths from DB
    for path in PATHS:
        if not os.path.isfile( path):
            print( '-', path)
            cur.execute( DELETE_SQL, (path,))

    def get_paths():
        for path in walk( dirs):
            assert len( path) < 255
            if path not in PATHS: yield path
    
    # Add fingerprints for new files at full throttle
    with multiprocessing.Pool() as pool:
        cur.executemany( INSERT_SQL,
            pool.imap_unordered( fingerprint, get_paths(), 2 * os.cpu_count()))
            

if __name__ == '__main__':
    
    parser = ArgumentParser( description='Scan music files.')
    parser.add_argument( 'file', nargs='*', help='Files or directories')
    args = parser.parse_args()

    try:
        conn = sqlite3.connect( DBPATH, isolation_level=None)
        cur = conn.cursor()
        scan( cur, args.file)
    finally:
        conn.close()
