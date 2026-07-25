"""Extraction — claims, evidence, and assumptions from full text.

v1 protocol (see the repository README):
  1. Manually review ~20 papers first to calibrate the claim schema.
  2. Then run model extraction over ~100 papers.
  3. Every extracted claim keeps a source location (section / page /
     paragraph / character offsets) so it can always be checked against
     the original text.
"""
