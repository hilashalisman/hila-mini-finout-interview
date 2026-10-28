# mini-finout

Cost data in from two sources, one table out, a dashboard on top.

```bash
python app/serve.py      # dashboard on :8080, Acme's Anthropic usage API on :8081
```

In a Codespace this starts on its own when the folder opens (see `.vscode/tasks.json`), and port
8080 is forwarded to your browser. Only run it yourself if you're working locally or the
auto-started task died. It needs nothing installed beyond Python.

```
TASK.md                  your ticket
DATA_DOCUMENTATION.md    the two sources, and the output the dashboard reads
CODE_STANDARDS.md        how code here is written

app/                     the dashboard and the Anthropic usage API - not yours, do not change
aws-export/              Acme's daily AWS cost export - your input, read-only
s3-storage-mock/         your local storage. the dashboard reads s3-storage-mock/output/
```

The pipeline is yours: any language, any structure, anywhere in the repo.
