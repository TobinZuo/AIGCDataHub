# Privacy and takedowns

Public web media may contain faces, locations, account handles, documents,
license plates, medical information, or other personal data. A production data
pipeline should:

- retain source identity and collection time;
- minimize unnecessary personal data in derived metadata;
- detect high-risk PII signals and route uncertain cases for review;
- provide a stable lookup from source/takedown identity to every derived sample;
- version deletion lists and propagate removals to shards, indexes, and caches;
- document retention, access control, and audit logs.

Hash-only removal systems should account for transformed copies and clips;
perceptual matching may be necessary, but it also needs human-reviewed thresholds.

