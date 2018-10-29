#!/usr/bin/env python3

'''
    Scan a music library
'''

from argparse import ArgumentParser
from curio import subprocess
import base64, curio, json, os, re, sqlite3


DBPATH = 'db.sqlite3'
AUDIO = set( ('.aac', '.flac', '.m4a', '.mp3', '.wav'))

INSERT_SQL = "INSERT INTO fingerprints (path, fp, duration) VALUES (?, ?, ?);"
SELECT_SQL = "SELECT path FROM fingerprints;"
DELETE_SQL = "DELETE FROM fingerprints WHERE path=?;"

BASEDIR = '/usr/local/radio'
PREFIX = re.compile( '^%s/' % BASEDIR)

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


async def fingerprint( path):
    'Get an AcoustID audio fingerprint'
    data = await subprocess.check_output( ['fpcalc', '-json', path])
        
    result = json.loads( str( data, 'UTF8'))
    fp = base64.b85decode( result['fingerprint'])
    duration = result['duration']
    
    trimmed = PREFIX.sub( '', path)
    print( trimmed, duration)
    return (trimmed, fp, duration)


async def scan( cur, dirs):
    'Synchronize the fingerprint database with the file system'
    
    # Fetch already processed paths
    cur.execute( SELECT_SQL)
    PATHS.update( row[0] for row in cur.fetchall())
    
    # Remove vanished paths from DB
    for path in PATHS:
        if not os.path.isfile( os.path.join( BASEDIR, path)):
            print( '-', path)
            cur.execute( DELETE_SQL, (path,))

    # Add fingerprints for new files at full throttle
    cpus = os.cpu_count()
    running = 0
    async with curio.TaskGroup() as tasks:
        for path in walk( dirs):
            trimmed = PREFIX.sub( '', path)
            assert len( trimmed) < 255

            if trimmed not in PATHS:
                if running == cpus:
                    # Limit number of subprocesses to available CPUs
                    t = await tasks.next_done()
                    running -= 1
                    cur.execute( INSERT_SQL, t.result)
                running += 1
                await tasks.spawn( fingerprint, path)
        # Collect remaining results
        async for t in tasks:
            cur.execute( INSERT_SQL, t.result)
            

if __name__ == '__main__':
    
    parser = ArgumentParser( description='Scan music files.')
    parser.add_argument( 'file', nargs='*', help='Files or directories')
    args = parser.parse_args()

    try:
        conn = sqlite3.connect( DBPATH, isolation_level=None)
        cur = conn.cursor()        
        curio.run( scan, cur, args.file)
    finally:
        conn.close()
