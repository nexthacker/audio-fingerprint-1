MUSIC = $(HOME)/Music/iTunes/iTunes Music/Music
DB    = db.sqlite3

.PHONY: scan dbshell clean tidy link

scan: $(DB)
	which fpcalc
	[ -d "$(MUSIC)" ]
	nice python3 scan.py "$(MUSIC)"

$(DB): schema.sql
	sqlite3 $@ < $<

dbshell: $(DB)
	sqlite3 $<

clean:
	rm -f $(DB)

link:
	$(MAKE) scan
	python3 dedup.py | bash -v
