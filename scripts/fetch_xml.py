"""Download IRS Form 990 e-file XML for the peer schools via HTTP-range reads of the IRS TEOS bulk zips."""
import zipfile_deflate64
import csv, glob, io, os, subprocess, sys, zipfile
EINS = {"911420530","910564971","371430960","910814431","910567266","910777610","910673111","910161095"}
BASE = "https://apps.irs.gov/pub/epostcard/990/xml"
OUT = sys.argv[1]; IDX = sys.argv[2]

class HttpFile(io.RawIOBase):
    def __init__(s, url):
        s.url, s.pos = url, 0
        h = subprocess.run(["curl","-sSIL","-m","60",url],capture_output=True,text=True).stdout.lower()
        s.size = int([l for l in h.splitlines() if l.startswith("content-length")][-1].split(":")[1])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s, o, w=0):
        s.pos = o if w==0 else s.pos+o if w==1 else s.size+o; return s.pos
    def readinto(s, b):
        n = min(len(b), s.size - s.pos)
        if n <= 0: return 0
        for _ in range(5):
            d = subprocess.run(["curl","-sSL","-m","300","-r",f"{s.pos}-{s.pos+n-1}",s.url],capture_output=True).stdout
            if len(d) == n: break
        b[:len(d)] = d; s.pos += len(d); return len(d)

def zips(year):
    if year in (2019, 2020): return [f"{year}_TEOS_XML_CT1"]+[f"download990xml_{year}_{i}" for i in range(1,9)]
    return [f"{year}_TEOS_XML_{i:02d}{s}" for i in range(1,13) for s in "AaBCD"]

want = {}
for f in glob.glob(IDX+"/idx20*.csv"):
    for r in csv.reader(open(f)):
        if r[2] in EINS and r[6] == "990": want[r[8]] = r[2]
print(len(want), "filings wanted")
byyear = {}
for oid in want: byyear.setdefault(int(oid[:4]), set()).add(oid)
for y, ids in sorted(byyear.items()):
    ids = {i for i in ids if not os.path.exists(f"{OUT}/{i}.xml")}
    for z in zips(y):
        if not ids: break
        url = f"{BASE}/{y}/{z}.zip"
        head = subprocess.run(["curl","-sS","-o","/dev/null","-w","%{http_code}","-r","0-1",url],capture_output=True,text=True).stdout
        if head != "206": continue
        zf = zipfile.ZipFile(io.BufferedReader(HttpFile(url), 1<<20))
        names = {os.path.basename(n).split("_public")[0]: n for n in zf.namelist()}
        for i in list(ids):
            if i in names:
                open(f"{OUT}/{i}.xml","wb").write(zf.read(names[i])); ids.discard(i); print("got", i, want[i], z, flush=True)
    if ids: print("MISSING", y, ids)
