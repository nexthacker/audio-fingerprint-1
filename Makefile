MUSIC = /usr/local/radio
BIN   = $(PWD)/.venv3/bin
DB    = db.sqlite3

.PHONY: scan dbshell clean tidy link

scan: $(DB) .venv3 $(MUSIC)
	nice $(BIN)/python3 scan.py "$(MUSIC)"

$(DB): schema.sql
	sqlite3 $@ < $<

dbshell: $(DB)
	sqlite3 $<

clean:
	rm -f $(DB)

tidy: clean
	rm -rf .venv3
	
link:
	$(MAKE) scan
	$(BIN)/python3 dedup.py | sh -v

.venv3: requirements.txt
	[ -d $@ ] || python3 -m venv $@
	$(BIN)/pip3 install -U pip
	$(BIN)/pip3 install -r $<
	touch $@
