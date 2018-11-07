#!/usr/bin/env python3

''' Replace duplicate audio files with hard links.
    No real action is taken, it simply prints a sequence 
    of commands that can be piped through a Posix shell.
'''

import os, sqlite3


DBPATH = 'db.sqlite3'
BASEDIR = '/usr/local/radio'
SELECT_SQL = """SELECT path, duration, fp FROM fingerprints
                WHERE duration > 90.0 AND duration < 300.0;"""

if __name__ == '__main__':
    
    try:
        conn = sqlite3.connect( DBPATH, isolation_level=None)
        cur = conn.cursor()
        
        d = {}
        cur.execute( SELECT_SQL)
        for path, dur, fp in cur.fetchall():
            if fp not in d: d[fp] = []
            d[fp].append( path)
        
        for fp in sorted( d):
            dups = sorted( d[fp])
            src = os.path.join( BASEDIR, dups[0])
            src_stat = os.stat( src)
            for dup in dups[1:]:
                tgt = os.path.join( BASEDIR, dup)
                tgt_stat = os.stat( tgt)
                if src_stat.st_ino != tgt_stat.st_ino:
                    print( "ln -f $'%s' $'%s'" % (
                        src.replace("'", "\\'"),
                        tgt.replace("'", "\\'")))
    finally:
        conn.close()

