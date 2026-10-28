# Your task

You're taking over the cost pipeline for **Acme Corp**.

Their cost comes from two sources:

- a daily **cost export from AWS**, delivered as files into `aws-export/`
- an **Anthropic usage API**

Both are described in `DATA_DOCUMENTATION.md`.

**Read it, then look at the data yourself - before you write any code.**

**We recommend planning your solution before you start coding.** Make sure you think about all
the requirements and edge cases.

---

## Requirements

1. **It works.** Run the pipeline, see the numbers on the dashboard.
2. **The numbers match** finance's tables in Part 1 and Part 2 (see below).
3. **Running it twice changes nothing.** We'll do exactly that at the end.
4. **It works tomorrow.** A new day, month or team needs no code changes.
5. **Remodeling doesn't refetch.** Changing a transformation never goes back to the API.

---

## Your environment

This is an interview, not production. Nobody expects a scale-ready system.

**Simple wins.** The plainest thing that works is exactly what we're hoping to see.

- **Your disk is your S3.** `s3-storage-mock/` stands in for a bucket. Keep raw copies,
  intermediate results, state and output there - plain files are all you need.
- **No database needed.** Plain lists and dicts are perfectly fine, and so are pandas, numpy,
  SQLite or DuckDB. You *can* set up a database server, but it'll eat time you'd rather spend
  elsewhere.
- **The export is already here.** Acme's AWS export is in `aws-export/` - no download, no
  credentials. Treat it as read-only input: never write to it.
- **No scheduler to build.** You run your command by hand whenever you want fresh numbers - and
  so will we.
- **The app is already running.** The dashboard and the Anthropic usage API are Acme's - leave
  `app/` as it is. If they're down: `python app/serve.py`.
- **One machine, one run at a time.** No parallel runs, no locking to worry about.
- **Install whatever you like.** Any language, any package.
- **The data is small.** A day fits in memory comfortably.

---

## Part 1 - AWS costs on the dashboard

Acme exports its AWS costs into **`aws-export/`** in this repo - one file per day. How it is laid
out and what is in it: `DATA_DOCUMENTATION.md`.

Read the export, model it, and write the output the dashboard reads.

- **Any structure.** The pipeline is yours.
- **One command runs it all.** Tell us what it is.
- **The output contract** is in `DATA_DOCUMENTATION.md`.

Refresh the dashboard to see your numbers. Until your pipeline writes output, it shows example
data - that disappears as soon as your first output file lands.

### Your numbers must match finance

August 2026, AWS cost export only:

| Team | Cost |
|:---|---:|
| platform | $134,612.79 |
| data | $103,760.75 |
| growth | $56,021.11 |
| ml | $148,794.44 |
| unallocated | $17,604.08 |
| **Total** | **$460,793.18** |

<sub>Each team is rounded to the cent on its own, so the teams add up to one cent less than the
total.</sub>

Three days, to check along the way:

| Day | Cost |
|:---|---:|
| 2026-08-17 | $16,716.38 |
| 2026-08-19 | $17,188.11 |
| 2026-08-25 | $18,201.89 |

If they don't match, something in the data isn't handled.

---

## Part 2 - add Anthropic usage

Add the usage API as a second source, into the same table. It runs next to the dashboard - try it:

```bash
curl "http://localhost:8081/usage?date=2026-08-01"
```

**The API fails now and then.** Your pipeline has to handle it.

### Your numbers with Anthropic in

August 2026, both sources:

| Source | `source` | Cost |
|:---|:---|---:|
| AWS cost export | `events` | $460,793.18 |
| Anthropic usage API | `anthropic` | $76,537.32 |
| **Total** | | **$537,330.50** |

| Team | Cost |
|:---|---:|
| platform | $145,835.22 |
| data | $123,187.48 |
| growth | $67,432.78 |
| ml | $183,270.93 |
| unallocated | $17,604.08 |
| **Total** | **$537,330.50** |

<sub>Each team is rounded to the cent on its own, so the teams add up to one cent less than the
total.</sub>

| Day | Cost |
|:---|---:|
| 2026-08-17 | $19,557.24 |
| 2026-08-19 | $20,069.23 |
| 2026-08-25 | $21,266.31 |

---

## Working with AI

You are free to use AI to help you with your code. You have an AI agent in the codespace and you are free to use it.

We expect you to be familiar with the code you write, and to be able to explain it fully.

**One hard rule: no AI may read Acme's data.**
Open it yourself, then describe what you found in your own words.

---

Ask us anything - about Acme, the data, or the repo.
