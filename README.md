# Votos granulares: São Paulo, Presidente 2026 (1º turno)

Mapa interativo com o resultado da eleição presidencial de 04/10/2026 **seção por seção** na cidade de São Paulo, a partir dos boletins de urna oficiais do TSE.

**Ver o mapa:** abra o `index.html` no navegador (ou a página do GitHub Pages deste repositório).

## O que o mapa mostra

- **Abas.** "1º turno", "2º turno" e "Diferença" (2º turno − 1º turno, local a local: variação de votos, da vantagem Lula−Flávio em pp e da abstenção).

- **Um ponto por local de votação.** A cor mostra a diferença entre Lula (13) e Flávio (22), em pontos percentuais dos votos válidos: vermelho quando Lula vence, azul quando Flávio vence, branco no empate. O tamanho do ponto cresce com o número de votos válidos.
- **Abstenção.** No modo "Abstenção" a cor muda para a taxa de abstenção (aptos que não compareceram): branco até 15%, roxo escuro a partir de 40%.
- **Detalhes.** Clique em um ponto, ou no 📍 da tabela, para abrir o painel à esquerda com os votos de todos os candidatos, brancos, nulos, comparecimento e abstenção.
- **Filtros.** Escolha "Total" ou uma zona eleitoral. A tabela pode listar seções ou locais e pode ser ordenada por Lula−Flávio ou por abstenção.

Locais com o mesmo nome **e exatamente a mesma coordenada** são somados num único ponto. Seções sem coordenada no cadastro do TSE ficam de fora.

## Dados

- **Votos:** boletins de urna (arquivos `-bu.dat`) publicados pelo TSE em [resultados.tse.jus.br](https://resultados.tse.jus.br).
- **Locais e coordenadas:** arquivo `eleitorado_local_votacao_2026_SP.csv` do [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br).
- **Mapa de fundo:** © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright).

Os nomes dos candidatos aparecem só para Lula e Flávio. Os demais aparecem pelo número. Para acrescentar nomes, edite `NOMES` em `mapa_template.html`.

Este é um projeto independente, sem vínculo com o TSE.

## Como refazer

São necessários Python 3 e [uv](https://docs.astral.sh/uv/) (ou pandas instalado).

1. Baixe `eleitorado_local_votacao_2026_SP.csv` do portal de dados abertos e coloque-o nesta pasta.
2. Baixe os boletins de urna (cerca de 27 mil seções, algumas horas):
   ```
   python3 scrape_bu.py        # 1º turno
   python3 scrape_bu.py 3221   # 2º turno
   ```
   O download é educado com o servidor: 3 conexões, pausa entre pedidos, e espera automática quando o servidor reclama. Se for interrompido, rode de novo: ele continua de onde parou. Seções que ainda não foram publicadas (erro 404) são puladas e podem ser baixadas depois rodando o script de novo.
3. Gere o mapa e os rankings:
   ```
   uv run --with pandas python mapa.py
   ```
   Isso cria `index.html`, `ranking.csv` (ordenado por Lula−Flávio) e `ranking_abstencao.csv`, mais as versões `_2turno`.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `scrape_bu.py` | Baixa os boletins de urna de todas as seções da cidade |
| `parse_bu.py` | Lê um `.dat` (formato ASN.1/BER do TSE) e devolve os votos em tabela |
| `mapa.py` | Junta votos e coordenadas e gera o mapa e os rankings |
| `mapa_template.html` | Página do mapa (Leaflet), preenchida pelo `mapa.py` |
| `index.html` | O mapa pronto (gerado, não edite à mão) |
| `ranking.csv`, `ranking_abstencao.csv` | Rankings das seções |

## Licença

Código sob [GPL-3.0](LICENSE). Os dados pertencem às respectivas fontes (TSE e OpenStreetMap).
