# RB-3 Bad deploy rollback

Symptoms: errors start within an hour after a deploy, NullPointerException or new exception types in the logs, the previous version was healthy.

Steps: freeze further deploys, compare the error start with the deploy time, roll back to the previous version after approval by the incident lead, confirm the error rate returns to baseline.
