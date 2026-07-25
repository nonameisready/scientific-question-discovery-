"""Question generation — candidate scientific questions from graph signals.

Inputs are the signals surfaced by the Evidence Graph competency queries:
contradictions, single-dataset conclusions, unexplained targets, and gaps
(objects/regimes present in catalogs but absent from the literature).

Each candidate question must carry the evidence that motivated it
(node/edge IDs), so refinement and falsification stay traceable.

Interface (implemented after the v1 graph is populated):

    generate_candidates(graph_dir) -> list[CandidateQuestion]

Target scale for v1: 50-200 candidate questions.
"""
