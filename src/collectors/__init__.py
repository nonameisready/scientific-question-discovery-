"""Collectors — layer 1 of the pipeline.

Each collector fetches from one external source and writes provenance-wrapped
JSONL (or raw files + a provenance sidecar) into data/raw/. Collectors never
transform data; normalization happens downstream.

    ads.py                 NASA ADS literature metadata (primary entry point)
    arxiv.py               arXiv preprint metadata (supplement to ADS)
    exoplanet_archive.py   NASA Exoplanet Archive planet/star catalog (TAP)
    mast.py                MAST observation *metadata* for JWST/HST (never bulk FITS)
"""
