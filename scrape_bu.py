"""Download every -bu.dat in SP / município 71072 / zonas 0251 (Pinheiros/Alto de Pinheiros) + 0346. Usage: python scrape_bu.py"""
import json, os, time, urllib.request
B = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3220"
UF, MU, ZONAS, OUT = "sp", "71072", ["0251", "0346"], "bus"
get = lambda u: urllib.request.urlopen(u, timeout=60).read()

cfg = json.loads(get(f"{B}/config/{UF}/{UF}-p003220-cs.json"))
mu = next(m for m in cfg["abr"][0]["mu"] if m["cd"] == MU)
secoes = [(z["cd"], s["ns"]) for z in mu["zon"] if z["cd"] in ZONAS for s in z["sec"]]
os.makedirs(OUT, exist_ok=True)
for ZN, ns in secoes:
    d = f"{B}/dados/{UF}/{MU}/{ZN}/{ns}"
    try:
        aux = json.loads(get(f"{d}/p003220-{UF}-m{MU}-z{ZN}-s{ns}-aux.json"))
    except Exception as e:
        print(ns, "aux fail", e); continue
    for h in aux.get("hashes", []):  # ponytail: >1 hash (urna replaced) saves all, newest wins on name clash
        for a in h["arq"]:
            p = f"{OUT}/{a['nm']}"
            if a["tp"] != "bu" or os.path.exists(p): continue
            open(p, "wb").write(get(f"{d}/{h['hash']}/{a['nm']}"))
            print(ns, a["nm"])
    time.sleep(0.2)
print(len(secoes), "seções")
