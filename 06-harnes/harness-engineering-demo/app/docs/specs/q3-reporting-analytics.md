# Q3 Epic: Reporting, Analytics & Export

> These are the **live-build targets** for the workshop. None of this is built yet.
> The workshop's Act 3 (system-gap skill) uses the CSV export as its guard subject.

## Tickets

### SCH-142 — Add CSV export to meetings page

**Route:** `GET /api/meetings/export?format=csv`

**Surface:** The `/meetings` page already has a PDF Export button
(`backend/app/api/routes_meetings.py`, line ~61). The workshop adds a "Export CSV"
button next to it.

**Pattern to follow:** `backend/app/services/export_service.py` — add a `CSVExport`
class alongside `PDFExport`, implementing the `ExportService` protocol.

**Code locations:**
- `backend/app/services/export_service.py` — add `CSVExport` class
- `backend/app/api/routes_meetings.py` — update the `export_meetings` route to
  dispatch to `CSVExport` when `format=csv`
- `frontend/app/meetings/page.tsx` — add Export CSV button (marked `TODO: SCH-142`)

**The formula-injection regression guard:**
A naive `CSVExport` implementation that writes user-controlled data (meeting title,
host name, notes) directly into CSV cells without escaping is vulnerable to
spreadsheet formula injection. A cell value starting with `=`, `+`, `-`, or `@` is
interpreted as a formula by Excel/Google Sheets. Example exploit: a meeting titled
`=HYPERLINK("http://evil.example","Click me")` would render as a live hyperlink.

The correct fix is to prefix such values with a single quote (`'`) or wrap them in
quotes and strip leading formula characters. The `/system-gap` skill in stage-3 is
trained to catch this pattern.

**Test guard (in `backend/app/tests/test_export.py`):**
```python
def test_csv_export_escapes_formula_injection():
    # Meeting with a formula-injection title
    # Assert the CSV output does NOT start a cell with "="
    ...
```

---

### SCH-201 — Reporting & Analytics dashboard

**Route:** `GET /analytics` (new page)

**Surface:** A dedicated analytics page (NOT the `/dashboard` operational KPIs page).
The dashboard shows real-time operational data (upcoming meetings, contacts, team
size). The analytics page shows historical trends.

**Planned metrics:**
- Meetings booked per week (last 12 weeks) — bar chart
- Meeting completion rate — line chart
- Stage distribution of contacts — donut chart
- Top hosts by meetings booked — ranked list
- Average meeting duration by host

**Backend:** New `GET /api/analytics/meetings` endpoint with `start`, `end` query
params for date-range filtering. Returns aggregated data (not raw rows).

**The date-range filter (SCH-202)** is a separate ticket — the initial analytics
page uses a fixed 90-day window. The workshop adds the filter UI.

---

### SCH-202 — Analytics date-range filter

**Depends on:** SCH-201

Add a date picker to the analytics page header that sets the `start` and `end`
query params on `GET /api/analytics/meetings`.

---

### SCH-204 — Weekly email digest

A scheduled job (cron/celery/APScheduler) that emails each team member a summary
of their upcoming week every Monday at 8 AM in their local timezone.

**Key challenge:** must use each user's `timezone` field to compute "Monday 8 AM
local" — cannot use a single UTC cron time for all users. This is a good
demonstration of why the `TimezoneAwareTime` helper matters at the infrastructure
level too.

---

## Notes on the CSV guard

The original stage-0 had a timezone rendering bug (SCH-203) as the regression guard.
That bug has been **fixed** — timezone handling is now correct using `TimezoneAwareTime`
throughout `meeting_service.py` and `export_service.py`.

The new guard for stage-3 is **CSV formula-injection escaping** (part of SCH-142).
The `/system-gap` skill should detect that the naive CSVExport implementation
doesn't sanitize cell values. The fix (prefix `'` or strip leading `=+@-`) is the
thing the skill proposes and the test suite validates.
