"""bus/*.dat + eleitorado CSV -> index.html (presidente) + ranking.csv + ranking_abstencao.csv"""
import glob, json
from collections import Counter
import pandas as pd
from parse_bu import parse_bu

df = pd.concat(pd.DataFrame(parse_bu(f)) for f in glob.glob("bus/*-bu.dat"))
p = df[(df.id_eleicao == 6257) & (df.cargo == 1)].copy()
p["label"] = p.numero.astype("Int64").astype(str).where(p.tipo_voto == "nominal", p.tipo_voto)
K = ["zona", "secao"]
sec = p.groupby(K).agg(local=("local", "first"), aptos=("aptos", "first"),
                       comparecimento=("comparecimento", "first")).reset_index()
votos = p.groupby(K + ["label"]).votos.sum()
sec["votos"] = [votos.loc[z, s].to_dict() for z, s in zip(sec.zona, sec.secao)]

geo = pd.read_csv("eleitorado_local_votacao_2026_SP.csv", sep=";", encoding="latin1", decimal=",",
                  usecols=["CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NM_LOCAL_VOTACAO", "DS_ENDERECO",
                           "NR_LATITUDE", "NR_LONGITUDE"])
geo = geo[geo.CD_MUNICIPIO == 71072].drop_duplicates(["NR_ZONA", "NR_SECAO"])
sec = sec.merge(geo, left_on=K, right_on=["NR_ZONA", "NR_SECAO"], how="left")
sec["id"] = sec.zona.astype(str) + "-" + sec.secao.astype(str)
sec["secoes"] = sec.id
print(len(sec), "seções;", sec.NR_LATITUDE.isna().sum(), "sem coordenada")


def recs(g):
    g = g.rename(columns={"NR_LATITUDE": "lat", "NR_LONGITUDE": "lon", "NM_LOCAL_VOTACAO": "nome", "DS_ENDERECO": "end"})
    g["lula"] = g.votos.map(lambda v: v.get("13", 0))
    g["flavio"] = g.votos.map(lambda v: v.get("22", 0))
    g["validos"] = g.votos.map(lambda v: sum(n for k, n in v.items() if k.isdigit()))
    g["dif"] = ((g.lula - g.flavio) / g.validos * 100).round(1)
    g["abst"] = g.aptos - g.comparecimento
    g["abst_pct"] = (g.abst / g.aptos * 100).round(1)
    return g.sort_values("dif", ascending=False)[["id", "nome", "end", "secoes", "lat", "lon", "lula", "flavio",
                                                  "validos", "dif", "aptos", "comparecimento", "abst", "abst_pct", "votos"]]


def locais(s):  # merge only same name AND exact same coordinate
    loc = (s.fillna({"NM_LOCAL_VOTACAO": "?"})
           .groupby(["NM_LOCAL_VOTACAO", "NR_LATITUDE", "NR_LONGITUDE"], dropna=False)
           .agg(DS_ENDERECO=("DS_ENDERECO", "first"), secoes=("id", lambda x: ", ".join(sorted(x))),
                aptos=("aptos", "sum"), comparecimento=("comparecimento", "sum"),
                votos=("votos", lambda vs: dict(sum(map(Counter, vs), Counter())))).reset_index())
    loc["id"] = loc.NM_LOCAL_VOTACAO + " " + loc.NR_LATITUDE.astype(str) + "," + loc.NR_LONGITUDE.astype(str)
    return loc


r = recs(sec)
cols = ["id", "nome", "lula", "flavio", "validos", "dif", "aptos", "comparecimento", "abst", "abst_pct"]
r[cols].to_csv("ranking.csv", index=False)
r.sort_values("abst_pct", ascending=False)[cols].to_csv("ranking_abstencao.csv", index=False)
print(r[r.id == "346-722"][["votos", "aptos", "comparecimento", "abst", "abst_pct"]].to_dict("records"))

scopes = {"total": sec} | {str(z): g for z, g in sec.groupby("zona")}
D = {k: {v: json.loads(recs(f(g)).to_json(orient="records")) for v, f in [("secao", lambda x: x), ("local", locais)]}
     for k, g in scopes.items()}
open("index.html", "w").write(open("mapa_template.html").read().replace("__DATA__", json.dumps(D)))
open("dispersao.html", "w").write(open("dispersao_template.html").read().replace("__DATA__", json.dumps(D["total"]["local"])))
