"""Historical validation — did the future agree the questions were worth asking?

Corpus A (exoplanet_atmospheres_v1) is bounded by cutoff_date 2020-12-31.
The validation corpus contains only 2021-2026 literature. For each ranked
question generated from Corpus A, this package retrieves the most relevant
post-cutoff papers and classifies the question's fate:

    answered              the community resolved it
    partially_addressed   substantial progress, core question open
    posed_but_open        the community asks the same question, unanswered
    not_addressed         no significant engagement found

A question the community independently posed or answered after the cutoff
is evidence the discovery pipeline surfaces questions worth asking — the
central claim the paper must support.
"""
