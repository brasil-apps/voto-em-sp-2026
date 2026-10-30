"""Download every -bu.dat (presidente/1º turno 2026) for the São Paulo município.
Polite: WORKERS threads, PAUSE seconds after each request; stops on the first 429/403/5xx. Resumable.
Usage: python scrape_bu.py [pleito]   (3220 = 1º turno, default; 3221 = 2º turno)"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

P = sys.argv[1] if len(sys.argv) > 1 else "3220"
B = f"https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/{P}"
UF, MU, OUT = "sp", "71072", "bus"
WORKERS, PAUSE = 6, 0.2  # ≈ 10 req/s at most; the run stops on the first sign TSE objects


def get(u):
    for tentativa in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "votos-granular (pesquisa)"}), timeout=60).read()
            time.sleep(PAUSE)
            return r
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            print("STOP: TSE respondeu", e.code, u, flush=True)  # server objecting: stop everything, rerun later
            os._exit(1)
        except Exception as e:  # timeout / connection reset: brief wait, then retry
            print("  retry", e, u, flush=True)
            time.sleep(30)
    raise RuntimeError(u)


def baixa(i, ZN, ns):
    if i % 500 == 0:
        print(i, "/", len(secoes), ZN, ns, flush=True)
    if os.path.exists(f"{OUT}/o0{P}{UF}{MU}{ZN}{ns}-bu.dat"):
        return  # already have it: skip the aux request too
    d = f"{B}/dados/{UF}/{MU}/{ZN}/{ns}"
    try:
        aux = json.loads(get(f"{d}/p00{P}-{UF}-m{MU}-z{ZN}-s{ns}-aux.json"))
        for h in aux.get("hashes", []):
            for a in h["arq"]:
                p = f"{OUT}/{a['nm']}"
                if a["tp"] == "bu" and not os.path.exists(p):
                    open(p + ".tmp", "wb").write(get(f"{d}/{h['hash']}/{a['nm']}"))
                    os.replace(p + ".tmp", p)  # atomic: a killed run never leaves a half file that looks done
    except Exception as e:
        print(ZN, ns, "fail", e, flush=True)


cfg = json.loads(get(f"{B}/config/{UF}/{UF}-p00{P}-cs.json"))
mu = next(m for m in cfg["abr"][0]["mu"] if m["cd"] == MU)
secoes = [(z["cd"], s["ns"]) for z in mu["zon"] for s in z["sec"]]
print(len(secoes), "seções", flush=True)
os.makedirs(OUT, exist_ok=True)
with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(lambda a: baixa(*a), ((i, z, s) for i, (z, s) in enumerate(secoes))))
print("done", len(secoes), "seções", flush=True)
