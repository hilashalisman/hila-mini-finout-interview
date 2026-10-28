# s3-storage-mock

Your local storage - it stands in for the bucket a real pipeline would write to.

Put anything you need here: raw copies of what you fetched, intermediate data, state. How you lay
it out is up to you. It is gitignored and safe to wipe.

One folder is fixed: **`output/`** is what the dashboard reads. The contract is in
`DATA_DOCUMENTATION.md`. `output/example.csv` is a sample with fake numbers - the dashboard shows
it until your pipeline writes its own output.
