# Learning episode and extractor review exports

CLIRec remains a recorder and episode supplier, not a learner. An episode uses
schema `clirec.episode.v1` and separates intention, demonstration steps,
optional approved annotations, expected outcome, actual outcome, confirmation,
corrections, references, consent, and local media links. Media bytes are never
embedded.

```bash
clirec episode-export recordings/demo.clirec --out episode.json \
  --goal "Save the document" --expected "File exists" \
  --actual "File exists" --confirmed --consent-export

clirec review-export episode.json --out skill-review.json --kind skill
clirec review-export episode.json --out workflow-review.json --kind workflow
```

`skill-extractor` is selected for a repeatable callable capability;
`workflow-extract` is selected for a periodic or self-running process. An
unclear case stays a briefing. Exports are machine-readable jobs for the
canonical instruction skills, not a parallel extractor API.

The review contract requires a confirmed outcome, path/person neutralization,
deduplication through “extend existing first,” and user review before extractor
approval. Workflow exports additionally require idempotence, locks, read-only
exit, log hygiene, cadence/budget review, and activation approval. A single
demonstration never becomes an active skill, policy, or scheduler job
automatically.

Gardener and USMC may receive approved metadata or a reviewed transcript;
BYUM receives only authorized corrections/outcomes. Raw audio is referenced
locally at most and is never ingested automatically.
