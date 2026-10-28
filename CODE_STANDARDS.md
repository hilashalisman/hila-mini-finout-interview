# Code standards

Whatever language you pick:

- Verbose names: verb + object. `build_raw_file_path`, `discover_available_days`.
- No nested calls that carry logic. Build the value, name it, pass it.
- No expressions in a `return`. Assign, then return.
- No comments unless something is genuinely non-obvious. Never multi-line.
- Typed, if the language lets you.
- One thing per module.
- Lines under 100 characters.
