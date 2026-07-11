# /validate skill (minimal)

Run the repo quality gate:

```bash
python scripts/validate.py
```

If validation fails:

1. Read failing test names
2. Fix only root causes
3. Re-run validation

Done means command exits with code 0.
