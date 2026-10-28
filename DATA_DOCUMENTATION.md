# Data documentation

Everything you need to know about Acme's two sources and the table you write. What to build is in
`TASK.md`.

**Acme's data is confidential, and no AI tool may read it.** Open it yourself - you should - and
describe what you found in your own words.

---

## Source 1 - the AWS cost export (`aws-export/`)

Acme exports its AWS cost report into `aws-export/` at the root of this repo, one file per day.
Each row is one line item of cost, charged to one of Acme's teams:

```
aws-export/date=<YYYY-MM-DD>/events.csv

timestamp     when the usage happened
team          the team being charged
service       what they used
cost_micros   what it cost, in millionths of a dollar
```

August 2026 is in the folder - 31 days of it, one `date=<YYYY-MM-DD>` folder per day. New days
arrive as new folders. The folder is Acme's input: read it, never write to it.

 Acme's export has never been through a billing-grade pipeline before. **Do not assume it
is clean.**

---

## Source 2 - the Anthropic usage API

Acme's Anthropic usage is not in the export. It comes from the Anthropic usage API, which runs
next to the dashboard (`app/serve.py` starts both):

```
GET http://localhost:8081/usage?date=<YYYY-MM-DD>

returns a JSON list, one record per call made to a model:

request_id    the call's id
timestamp     when the call was made
team          the team being charged
model         which model was called
tokens        how many tokens the call used
```

- **It reports usage, not money.** Every token costs the same: **$3.00 per 1M tokens**.
- **It is not reliable.** Roughly 1 in 50 calls fails with a `500`.
- A malformed date gets a `400`. A day with no usage returns an empty list.

---

## Data assumptions

Acme's rules about their own data, so you do not have to guess at their intent:

- **Team names are not case sensitive.** `Platform` and `platform` are the same team.

---

## The output - what the dashboard reads

The dashboard reads **every `.csv` file under `s3-storage-mock/output/`**, at any depth, and adds
them all up. One file or one per day - your call. Every file starts with this header:

```
date,source,team,service,cost

date      YYYY-MM-DD
source    events | anthropic
team      the team being charged
service   what they used
cost      in dollars, e.g. 1234.567891
```

**Write `cost` at full precision - do not round it.** The dashboard adds rows up, and rounding
each row to cents drifts the totals by a few cents away from finance's numbers.

**`output/example.csv`** is a sample in this format, with fake numbers. The dashboard shows it
only while it is the only CSV there, and ignores it as soon as your pipeline writes its own.

- `source` - where the cost came from: `events` for the AWS cost export, `anthropic` for the
  Anthropic usage API.
- `service` - for AWS, the line item's `service`; for Anthropic, the `model`.
- `team` - `unallocated` is finance's name for cost they could not attribute to a team. They still
  want to see it.
