"""Parse downloaded IRS 990 XML into data/peers.json (one record per school per fiscal year; FY = year the fiscal year ends)."""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET

SCHOOLS = {
    "911420530": "The Bear Creek School", "910564971": "Lakeside School", "371430960": "Eastside Preparatory School",
    "910814431": "Overlake School", "910567266": "Annie Wright Schools", "910777610": "Seattle Country Day School",
    "910673111": "Charles Wright Academy", "910161095": "The Bush School",
}
PART1 = {"contrib": "ContributionsGrantsAmt", "program": "ProgramServiceRevenueAmt", "invest": "InvestmentIncomeAmt",
         "other": "OtherRevenueAmt", "revenue": "TotalRevenueAmt", "comp": "SalariesCompEmpBnftPaidAmt", "expenses": "TotalExpensesAmt"}

ENDOW = {"begin": "BeginningYearBalanceAmt", "gifts": "ContributionsAmt", "earnings": "InvestmentEarningsOrLossesAmt",
         "grants": "GrantsOrScholarshipsAmt", "other": "OtherExpendituresAmt", "admin": "AdministrativeExpensesAmt", "end": "EndYearBalanceAmt"}

def strip(t): return t.split("}")[-1]

def first(root, name):
    for e in root.iter():
        if strip(e.tag) == name: return e
def num(root, name):
    e = first(root, name) if root is not None else None
    return int(float(e.text)) if e is not None and e.text else None

def parse(path):
    root = ET.parse(path).getroot()
    ein = first(root, "EIN").text
    end = first(root, "TaxPeriodEndDt").text
    fy = int(end[:4]); rows = {}
    for prefix, yr in (("CY", fy), ("PY", fy - 1)):
        r = {k: num(root, prefix + v) for k, v in PART1.items()}
        r["src"] = os.path.basename(path)[:-4]; r["own"] = prefix == "CY"
        rows[yr] = r
    rows[fy]["netassets"] = num(root, "NetAssetsOrFundBalancesEOYAmt")
    rows[fy - 1]["netassets"] = num(root, "NetAssetsOrFundBalancesBOYAmt")
    endow = {}
    for i, tag in enumerate(["CYEndwmtFundGrp", "CYMinus1YrEndwmtFundGrp", "CYMinus2YrEndwmtFundGrp", "CYMinus3YrEndwmtFundGrp", "CYMinus4YrEndwmtFundGrp"]):
        g = first(root, tag)
        if g is not None:
            endow[fy - i] = {k: num(g, t) or 0 for k, t in ENDOW.items()}
            if num(g, "EndYearBalanceAmt") is None: del endow[fy - i]
    return ein, rows, endow

data = {e: {} for e in SCHOOLS}
endow = {e: {} for e in SCHOOLS}
for p in sorted(glob.glob(sys.argv[1] + "/*.xml")):
    ein, rows, en = parse(p)
    for yr, r in rows.items():
        cur = data[ein].get(yr)
        if cur is None or (r["own"] and not cur["own"]) or (r["own"] == cur["own"] and r["src"] > cur["src"]): data[ein][yr] = r
    for yr, v in en.items(): endow[ein][yr] = v  # later filings processed last (sorted by object id) overwrite restated values
out = {}
for ein, name in SCHOOLS.items():
    out[ein] = {"name": name, "years": {str(y): {**{k: r[k] for k in list(PART1) + ["netassets"]}, "endow": endow[ein].get(y)} for y, r in sorted(data[ein].items())}}
os.makedirs("data", exist_ok=True)
json.dump(out, open("data/peers.json", "w"), indent=1)
for ein, o in out.items():
    print(o["name"]); 
    for y, r in o["years"].items(): print(" ", y, r["endow"])
