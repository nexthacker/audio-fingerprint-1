# Audio fingerprinting with [Chromaprint](https://acoustid.org/chromaprint)

This is a small [utility](scan.py) to collect [Chromaprint](https://acoustid.org/chromaprint) fingerprints from music files. They are stored in a [sqlite](https://sqlite.org/index.html) database. An [example](dedup.py) is included that uses the fingerprint database to find exact duplicates (ignoring any metadata and encoding changes).

`fpcalc` is expected in the system `PATH`. You can download it from [acoustid.org](https://acoustid.org/chromaprint). Because fingerprinting can be a bit slow, the scanner uses all available CPUs in parallel.

For real-world usage, see the [Makefile](Makefile).

