"""Falsification — evidence-based question refinement.

For each candidate question, attempt to kill it cheaply before it reaches
ranking:

  * Catalog check: is the claimed pattern general, or an artifact of a few
    special targets? (NASA Exoplanet Archive tables)
  * Observation check: does existing MAST metadata show the question is
    already answerable — or already answered — by archived data?
  * Literature check: has a later paper already resolved it?

Only when a question survives these checks (and is selected) do we download
the corresponding high-level data products on demand.

Interface (implemented after question_generation):

    falsify(question, evidence_context) -> FalsificationVerdict
"""
