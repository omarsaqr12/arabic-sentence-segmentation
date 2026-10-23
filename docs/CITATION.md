# Which work should I cite?

This repository contains the original encoder/structured-decoding project and a
separately attributed, commit-pinned ENSAR research integration. They have
different manuscript records.

## Original encoder and decoding work

The checked-in [standalone manuscript source](../paper/araseg_system.tex) credits
**Team omar_saqr** and is titled *Saturation as a Result: Ensembling, Length-Prior
Decoding, and the Data Ceiling in Arabic Sentence Segmentation*.

The root [CITATION.cff](../CITATION.cff) uses that recorded team attribution for
the original work. It no longer names the unsupported individual **Omar Ganna**.
The manuscript source does not establish an individual author list, so repository
ownership is not used to invent one. Its preferred citation is marked
**unpublished** because this checkout does not establish an archival proceedings
record for that standalone draft.

## ENSAR

The pinned [ENSAR manuscript](https://github.com/noortaytoy1/araseg-competition/blob/122f50214f66c2dd5628a06fa2449783d7368e4b/paper/ensar_araseg.tex) lists,
in order:

1. Noor Emam
2. Omar Saqr
3. Mostafa Gafaar
4. Aly El-aswad

Its title is *ENSAR at AraSeg Shared Task 2026: An Ensemble of Encoders With
Agentic Error Refinement*. The integration's upstream snapshot is
`122f50214f66c2dd5628a06fa2449783d7368e4b`.

For that checked-in manuscript snapshot, a citation is:

```bibtex
@unpublished{emam2026ensar,
  author = {Noor Emam and Omar Saqr and Mostafa Gafaar and Aly El-aswad},
  title = {{ENSAR} at {AraSeg} Shared Task 2026:
           An Ensemble of Encoders With Agentic Error Refinement},
  year = {2026},
  note = {Public manuscript snapshot at commit
          122f50214f66c2dd5628a06fa2449783d7368e4b},
  url = {https://github.com/noortaytoy1/araseg-competition/blob/122f50214f66c2dd5628a06fa2449783d7368e4b/paper/ensar_araseg.tex}
}
```

Use an authoritative final proceedings record when citing the archival paper.
This entry describes the public snapshot and adds no unverified DOI, pages or
publication status. The upstream manuscript's contact placeholders, history,
licensing and author list were not edited.

See [ENSAR integration and reproducibility](ENSAR_INTEGRATION.md) for evaluation
populations, saved-verdict replay and the documented data-exposure/remediation
history. A correct citation does not independently validate experimental results.

