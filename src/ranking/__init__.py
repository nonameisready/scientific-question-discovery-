"""Ranking — from surviving candidates to ranked high-value questions.

Scoring dimensions (shared with the evaluation rubric in evaluations/):

  novelty       Not a paraphrase of an existing question in the corpus.
  feasibility   Answerable with existing or plausible near-term observations.
  significance  Resolving it would change conclusions of multiple papers.
  clarity       Precise enough to design a falsification test against.

Output for v1: a ranked list with per-dimension scores and the evidence
trail for each question. Target: top 10-20 questions from 50-200 candidates.

Interface (implemented after falsification):

    rank(questions) -> list[RankedQuestion]
"""
