# Validation

Recorded 2026-10-29 on Stable Studionet, chain **61999**, RPC **https://studio.genlayer.com/api**.

## Local tests: simulated semantics

- **11 unit tests passed**, including 729 small three-event networks checked against independent enumeration of every integer schedule within a four-minute horizon. Feasibility and tight ranges matched the oracle. Negative-cycle witnesses were checked by code.
- Ownership, digest guards, immutability, repeat compilation/certification, ambiguity, malformed outputs and independent validator disagreement passed.
- Official linter: 3 checks passed; SDK validation passed; 5 public methods (3 write, 2 view).
- Pinned official SDK Direct Mode passed storage/calldata, feasible proof, validator acceptance and rejection, and terminal certification, with a mocked LLM.

These are local tests, not evidence of actual validator consensus or general model accuracy.

## Real network evidence

Contract: `0xA090568E1a68800611D730C858A8747fc41AF893`.
Source SHA-256: `734301ce9ce4b61ffec25eb70b28d368ac7956d3379daa5bae3184827f8027c0`.

Four distinct full-consensus transactions completed with **FINALIZED / MAJORITY_AGREE / SUCCESS** and `leader_only=false`. Zero-value writes; no cash funding, Appeal or transaction resend.

| Step | Transaction hash |
| --- | --- |
| deploy | `0x0d29fe36d546ffdb679d37b2dea04c63e28b4b1c2a66abfc6f2b242427d50131` |
| seal | `0x506f49bf5f1421990afefb444ec74e6600c918d1346a27d07ff860b76209bb98` |
| compile | `0xe35e6332b75c44b829c29c9807229e37375503446d51ce60e4bb99647e051716` |
| certify | `0x3c3ae6b97982e633aa30da94f4235deae4c50cdd52198ce5d2eba4085525a857` |

The synthetic archive schedule ended **CERTIFIED** with feasible witness `[0, 30, 150]` and tight per-event ranges `[[0, 0], [30, 60], [150, 180]]`. Event 0 is the origin. Deployed source was compared byte-for-byte with the source file. Public receipt projections and the complete final record are in [evidence/studionet.json](evidence/studionet.json).

One receipt read after the compile submission returned non-JSON upstream connection text. The original hash was checked read-only and was already FINALIZED / MAJORITY_AGREE / SUCCESS. Tracking resumed that same hash, then submitted the previously unperformed certification. There was no second compile transaction. This was a transport interruption, not a failed consensus result.

Only the feasible fixture was tested on chain. Negative-cycle, ambiguous and malicious-format cases were tested locally; no live result is claimed for those paths. Inputs are synthetic owner declarations. A certificate proves mathematical feasibility relative to accepted compiled bounds, not real-world timing or universal semantic correctness.

`node scripts/read-live.mjs` independently fetches the original transaction receipts and finalized record without signing. It checks chain ID, exact source bytes, sender/target/method/argument binding, full-consensus finality and execution, content digest and schedule constraints. It does not repeat a transaction.
