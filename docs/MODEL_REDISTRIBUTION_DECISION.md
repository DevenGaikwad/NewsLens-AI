# Model Redistribution Decision

## Current decision

The public repository and Streamlit deployment may include `models/newslens_synthetic_pipeline.joblib` and `models/newslens_synthetic_calibration.json` because they were created solely from the independently authored synthetic benchmark and are documented and hash-bound in the public artifact manifest.

## Historical private artifact

The private ISOT-derived classifier and calibration remain permanently excluded. No inference, coefficient, vocabulary, prediction, calibration parameter, or benchmark result from those artifacts was transferred into the public model. Replacement with a synthetic-only workflow resolves the deployment gate without asserting rights over the earlier material.

Download availability or noncommercial student status is not treated as redistribution permission.
