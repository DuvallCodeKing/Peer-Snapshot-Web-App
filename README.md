# Bear Creek Peer Snapshot

One-page peer comparison of The Bear Creek School against seven Puget Sound independent schools, built from IRS Form 990 e-file data (FY2018–FY2025).

Open `index.html` in a browser (no server or build step needed; data is inlined).

## Rebuilding
1. `python3 scripts/fetch_xml.py <xml_dir> <index_dir>` – downloads each school's 990 XML from the IRS TEOS bulk zips (needs the IRS `index_YYYY.csv` files in `<index_dir>`; requires `zipfile-deflate64`).
2. `python3 scripts/build_data.py <xml_dir>` – writes `data/peers.json`.
3. `python3 scripts/build_site.py` – inlines the data into `index.html` (from `scripts/template.html`).

## Definitions
- Operating margin = (revenue − investment income − expenses) ÷ (revenue − investment income)
- Salaries & benefits = Part I line 15 ÷ total expenses
- Endowment = Schedule D Part V year-end balance; implied draw = (grants + other + admin) ÷ beginning balance
