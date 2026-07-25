"""Scientific Question Discovery — pipeline source code.

Pipeline stages (mirrors the architecture in the top-level README):

    collectors/          Existing scientific knowledge (literature, catalogs, observations)
    normalization/       Evidence representation (relational tables)
    extraction/          Claims and their support/assumptions from full text
    evidence_graph/      Contradictions, gaps, alternative explanations
    question_generation/ Candidate scientific questions from graph signals
    falsification/       Evidence-based question refinement
    ranking/             Ranked high-value scientific questions
"""
