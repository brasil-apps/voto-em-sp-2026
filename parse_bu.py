"""Parse a TSE boletim de urna (.dat / -bu.dat) into tidy rows. No dependencies."""
import sys, csv

TIPO_VOTO = {1: "nominal", 2: "branco", 3: "nulo", 4: "legenda", 5: "cargo_sem_candidato"}


def _tlv(b, i):
    t = b[i]; i += 1
    num = t & 0x1F
    if num == 0x1F:
        num = 0
        while True:
            x = b[i]; i += 1
            num = (num << 7) | (x & 0x7F)
            if not x & 0x80:
                break
    l = b[i]; i += 1
    if l & 0x80:
        n = l & 0x7F
        l = int.from_bytes(b[i:i + n], "big"); i += n
    return t, num, b[i:i + l], i + l


def items(b):
    out, i = [], 0
    while i < len(b):
        t, num, v, i = _tlv(b, i)
        out.append(("UACP"[t >> 6], num, bool(t & 0x20), v))
    return out


def as_int(v):
    return int.from_bytes(v, "big", signed=True)


def find(elems, cls, tag):
    return next(v for c, n, _, v in elems if c == cls and n == tag)


def parse_bu(path):
    raw = open(path, "rb").read()
    env = items(items(raw)[0][3])
    bu = items(items(find(env, "U", 4))[0][3])
    seqs = [v for c, n, k, v in bu if c == "U" and n == 16]
    ident = items(seqs[2])
    mz = items(ident[0][3])
    municipio, zona = as_int(mz[0][3]), as_int(mz[1][3])
    local, secao = as_int(ident[1][3]), as_int(ident[2][3])
    rows = []
    for _, _, _, eleicao in items(seqs[3]):
        e = items(eleicao)
        id_eleicao, aptos = as_int(e[0][3]), as_int(e[1][3])
        for _, _, _, rv in items(find(e, "U", 16)):
            r = items(rv)
            comparecimento = as_int(r[1][3])
            for _, _, _, tvc in items(r[2][3]):
                t = items(tvc)
                cargo = as_int(find(t, "C", 1))
                for _, _, _, vv in items(find(t, "U", 16)):
                    x = items(vv)
                    numero = None
                    try:
                        numero = as_int(items(find(x, "C", 3))[1][3])
                    except StopIteration:
                        pass
                    rows.append(dict(municipio=municipio, zona=zona, local=local, secao=secao,
                                     id_eleicao=id_eleicao, cargo=cargo, aptos=aptos,
                                     comparecimento=comparecimento,
                                     tipo_voto=TIPO_VOTO.get(as_int(find(x, "C", 1))),
                                     numero=numero, votos=as_int(find(x, "C", 2))))
    return rows


if __name__ == "__main__":
    rows = parse_bu(sys.argv[1])
    w = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
