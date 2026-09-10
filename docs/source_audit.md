# Public provenance and security audit

This note records bounded checks of the public package and its cited upstream source. It is an evidence log, not a claim that every possible security property has been proven.

## Upstream attribute provenance

The OSF node `f29be` was queried through the public API. Its `osfstorage` file relationship contains `Code and Data.zip` (OSF file id `67f0879e25cbac45426ddfe9`, download guid `3aybh`). The archive was downloaded and its file listing was searched recursively. The relevant path is:

`Code and Data/2 - Vectorize Reasons/attributes.csv`

The extracted file has SHA-256 `7491faea757869d926553c111f740555e5e1ac52abcb955a13315d53fb93f945`, matching [`data/bhatia/attributes.csv`](../data/bhatia/attributes.csv). The archive SHA-256 was `7aaa83032ccb7f64eae4b833e505b9bd746f62792fbaf1c1e2aa23c7da31ebf8`; the OSF API metadata identifies the same public archive. The companion macOS metadata entry (`._attributes.csv`) was not used.

The [OSF node API](https://api.osf.io/v2/nodes/f29be/) and [license API](https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e972/) were separately checked during release preparation: the project is public and MIT licensed, with the 2024 copyright holders recorded in [`NOTICE`](../NOTICE). This repository does not redistribute the Bhatia article PDF.

## Local artifact checks

- `find . -type l` returned no symbolic links.
- All staged `.npz` files were opened with `allow_pickle=False`. `study/original/results/main_vectors.npz` contains `ids (720,)`, `embedding (720,384)`, `concept207 (720,207)`, and `hybrid50 (720,591)`, all numeric except the string IDs. `study/original/data/anchors_multi.npz` contains `anchors (207,384)` and string `names (207,)`.
- A bounded scan of staged text and source files found no credential markers, private-key blocks, bearer/authorization values, or actual local absolute paths. Matches for the words “limit”, “token”, and model metadata describe the experiment and are not secrets.
- [`docs/source_transformations.json`](source_transformations.json) records 194 original artifacts: 191 byte-identical artifacts and three documented path-only/output-warning edits. The frozen input count is 32 and the design-hash count is 8. The original verification manifest remains at [`study/source-verification.json`](../study/source-verification.json).

The scan does not establish that arbitrary future files or dynamically generated outputs are safe; it documents the checked staged tree at audit time.
