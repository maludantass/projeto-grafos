"""
Constrói um grafo de similaridade musical a partir do Spotify Tracks Dataset.

Nós: músicas (identificadas por track_id)
Arestas: conectam músicas similares (distância euclidiana entre atributos normalizados)
Peso: distância euclidiana (quanto menor, mais similar)
Tipo: não dirigido e ponderado

Saída (em data/dataset_parte2/):
  - musicas_nos.csv          → nós do grafo com atributos
  - adjacencias_musicas.csv  → arestas (pares de músicas similares com peso)
  - descricao_dataset.txt    → descrição exigida (|V|, |E|, tipo, distribuição de graus)
"""

import csv
import json
import os
import sys
import random
import math
from collections import Counter
from pathlib import Path

GENRE_MAP = {
    # pop
    "indie-pop": "pop", "synth-pop": "pop",
    # rock
    "alt-rock": "rock", "alternative": "rock",
    # hip-hop
    "r-n-b": "hip-hop", "soul": "hip-hop",
    # electronic
    "edm": "electronic", "dance": "electronic",
    # funk
    "disco": "funk",
    # brazil
    "mpb": "brazil", "sertanejo": "brazil", "samba": "brazil",
    "pagode": "brazil", "forro": "brazil", "brazil": "brazil",
    # latin
    "latino": "latin", "reggaeton": "latin",
}

# apenas músicas cujo gênero original está nesta lista
GENEROS_PERMITIDOS = {
    "pop", "rock", "hip-hop", "r-n-b", "dance", "edm", "electronic",
    "indie-pop", "alternative", "alt-rock", "synth-pop", "disco", "funk",
    "soul", "country", "latino", "reggaeton", "mpb", "sertanejo",
    "samba", "pagode", "forro", "brazil",
}

ATRIBUTOS_SIMILARIDADE = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence",
]

ATRIBUTOS_NORMALIZAR = ["loudness", "tempo"]

TAMANHO_AMOSTRA = 4000
K_VIZINHOS = 7
SEED = 42


def ler_dataset(caminho_csv):
    por_musica = {}
    with open(caminho_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            track_id = linha.get("track_id", "").strip()
            if not track_id:
                continue
            try:
                atributos = {}
                for attr in ATRIBUTOS_SIMILARIDADE + ATRIBUTOS_NORMALIZAR:
                    atributos[attr] = float(linha[attr])
                genero_raw = linha.get("track_genre", "").strip()
                if genero_raw not in GENEROS_PERMITIDOS:
                    continue
                genero = GENRE_MAP.get(genero_raw, genero_raw)
                popularidade = int(linha.get("popularity", 0))
                track_name = linha.get("track_name", "").strip()
                artists = linha.get("artists", "").strip()
                # chave de deduplicação: mesma música mesmo em álbuns diferentes
                chave = (track_name.lower(), artists.lower())
                musica = {
                    "track_id": track_id,
                    "track_name": track_name,
                    "artists": artists,
                    "track_genre": genero,
                    "popularity": popularidade,
                    **atributos,
                }
                if chave not in por_musica or popularidade > por_musica[chave]["popularity"]:
                    por_musica[chave] = musica
            except (ValueError, KeyError):
                continue
    return list(por_musica.values())


def amostrar_por_genero(musicas, tamanho, seed):
    rng = random.Random(seed)
    por_genero = {}
    for m in musicas:
        por_genero.setdefault(m["track_genre"], []).append(m)

    generos = sorted(por_genero.keys())
    por_genero_qtd = max(1, tamanho // len(generos))

    amostra = []
    for g in generos:
        pool = por_genero[g]
        n = min(por_genero_qtd, len(pool))
        amostra.extend(rng.sample(pool, n))

    while len(amostra) < tamanho:
        g = rng.choice(generos)
        candidato = rng.choice(por_genero[g])
        if candidato["track_id"] not in {m["track_id"] for m in amostra}:
            amostra.append(candidato)

    rng.shuffle(amostra)
    return amostra[:tamanho]


def normalizar_atributos(musicas):
    mins = {}
    maxs = {}
    for attr in ATRIBUTOS_NORMALIZAR:
        valores = [m[attr] for m in musicas]
        mins[attr] = min(valores)
        maxs[attr] = max(valores)

    for m in musicas:
        for attr in ATRIBUTOS_NORMALIZAR:
            span = maxs[attr] - mins[attr]
            if span == 0:
                m[attr + "_norm"] = 0.0
            else:
                m[attr + "_norm"] = (m[attr] - mins[attr]) / span


def distancia_euclidiana(m1, m2):
    soma = 0.0
    for attr in ATRIBUTOS_SIMILARIDADE:
        soma += (m1[attr] - m2[attr]) ** 2
    for attr in ATRIBUTOS_NORMALIZAR:
        soma += (m1[attr + "_norm"] - m2[attr + "_norm"]) ** 2
    return math.sqrt(soma)


def construir_arestas_knn(musicas, k):
    """Conecta cada música aos K vizinhos mais próximos dentro do mesmo gênero."""
    import numpy as np
    from collections import defaultdict

    attrs = ATRIBUTOS_SIMILARIDADE + [a + "_norm" for a in ATRIBUTOS_NORMALIZAR]

    por_genero = defaultdict(list)
    for i, m in enumerate(musicas):
        por_genero[m["track_genre"]].append(i)

    arestas_set = set()
    arestas = []

    X = np.array([[m[a] for a in attrs] for m in musicas], dtype=np.float32)

    for genero, indices in por_genero.items():
        if len(indices) < 2:
            continue
        k_local = min(k, len(indices) - 1)
        Xg = X[indices]

        diff = Xg[:, None, :] - Xg[None, :, :]
        dists = np.sqrt((diff ** 2).sum(axis=2))
        np.fill_diagonal(dists, np.inf)

        print(f"  {genero}: {len(indices)} musicas, K={k_local}")

        for li, gi in enumerate(indices):
            vizinhos_locais = np.argpartition(dists[li], k_local)[:k_local].tolist()
            for lj in vizinhos_locais:
                gj = indices[lj]
                chave = (min(gi, gj), max(gi, gj))
                if chave not in arestas_set:
                    arestas_set.add(chave)
                    arestas.append({
                        "origem": musicas[gi]["track_id"],
                        "destino": musicas[gj]["track_id"],
                        "peso": round(float(dists[li, lj]), 6),
                    })

    return arestas


def calcular_distribuicao_graus(arestas, musicas):
    graus = Counter()
    ids = {m["track_id"] for m in musicas}
    for tid in ids:
        graus[tid] = 0
    for a in arestas:
        graus[a["origem"]] += 1
        graus[a["destino"]] += 1
    return graus


def salvar_nos_csv(musicas, caminho):
    campos = [
        "track_id", "track_name", "artists", "track_genre", "popularity",
        *ATRIBUTOS_SIMILARIDADE, *ATRIBUTOS_NORMALIZAR,
    ]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(musicas)


def salvar_arestas_csv(arestas, caminho):
    campos = ["origem", "destino", "peso"]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(arestas)


def salvar_descricao(musicas, arestas, graus, caminho):
    num_v = len(musicas)
    num_e = len(arestas)

    valores_grau = list(graus.values())
    grau_min = min(valores_grau)
    grau_max = max(valores_grau)
    grau_medio = sum(valores_grau) / len(valores_grau)

    freq_grau = Counter(valores_grau)

    pesos = [a["peso"] for a in arestas]
    peso_min = min(pesos)
    peso_max = max(pesos)
    peso_medio = sum(pesos) / len(pesos)

    generos = Counter(m["track_genre"] for m in musicas)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=" * 65 + "\n")
        f.write("DESCRICAO DO DATASET — PARTE 2 (Spotify Tracks)\n")
        f.write("=" * 65 + "\n\n")

        f.write("FONTE: Spotify Tracks Dataset (Kaggle)\n")
        f.write("https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset\n\n")

        f.write("CONSTRUCAO DO GRAFO:\n")
        f.write(f"  - Dataset original: 114.000 faixas\n")
        f.write(f"  - Amostra utilizada: {num_v} musicas (estratificada por genero)\n")
        f.write(f"  - Nos: cada musica e um vertice\n")
        f.write(f"  - Arestas: K-vizinhos mais proximos (K={K_VIZINHOS}) por similaridade\n")
        f.write(f"  - Peso: distancia euclidiana entre vetores de atributos normalizados\n")
        f.write(f"  - Atributos usados: {', '.join(ATRIBUTOS_SIMILARIDADE + ATRIBUTOS_NORMALIZAR)}\n\n")

        f.write("PROPRIEDADES DO GRAFO:\n")
        f.write(f"  |V| (vertices)  = {num_v}\n")
        f.write(f"  |E| (arestas)   = {num_e}\n")
        f.write(f"  Tipo            = Nao dirigido, Ponderado\n")
        f.write(f"  Pesos           = Distancia euclidiana (continuo)\n")
        f.write(f"    Peso minimo   = {peso_min:.6f}\n")
        f.write(f"    Peso maximo   = {peso_max:.6f}\n")
        f.write(f"    Peso medio    = {peso_medio:.6f}\n\n")

        f.write("DISTRIBUICAO DE GRAUS:\n")
        f.write(f"  Grau minimo  = {grau_min}\n")
        f.write(f"  Grau maximo  = {grau_max}\n")
        f.write(f"  Grau medio   = {grau_medio:.2f}\n\n")

        f.write("  Frequencia por grau:\n")
        f.write(f"  {'Grau':>6}  {'Qtd vertices':>14}  {'%':>8}\n")
        f.write(f"  {'-'*6}  {'-'*14}  {'-'*8}\n")
        for g in sorted(freq_grau.keys()):
            pct = 100 * freq_grau[g] / num_v
            f.write(f"  {g:>6}  {freq_grau[g]:>14}  {pct:>7.2f}%\n")

        f.write(f"\nGENEROS NA AMOSTRA:\n")
        for gen, qtd in sorted(generos.items()):
            f.write(f"  {gen:<20} {qtd:>4} musicas\n")

    print(f"  Descricao salva em: {caminho}")


def gerar_graph_json(musicas, arestas, graus, caminho):
    """Gera graph.json para o frontend (nodes + edges com value = 1 - peso)."""
    nodes = [
        {
            "id": m["track_id"],
            "name": m["track_name"],
            "artist": m["artists"],
            "genre": m["track_genre"],
            "popularity": m["popularity"],
            "degree": graus.get(m["track_id"], 0),
        }
        for m in musicas
    ]
    edges = [
        {
            "source": a["origem"],
            "target": a["destino"],
            "value": round(1.0 - a["peso"], 6),
        }
        for a in arestas
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False)
    print(f"  graph.json salvo em: {caminho}")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "dataset_parte2" / "dataset_parte2.csv"
    out_dir = base_dir / "data" / "dataset_parte2"

    if not csv_path.exists():
        print(f"Erro: arquivo nao encontrado: {csv_path}")
        sys.exit(1)

    print("=" * 55)
    print("CONSTRUINDO GRAFO DE SIMILARIDADE MUSICAL")
    print("=" * 55)

    print(f"\n[1] Lendo dataset: {csv_path.name}")
    musicas = ler_dataset(str(csv_path))
    print(f"    {len(musicas)} musicas lidas com sucesso.")

    print(f"\n[2] Amostrando {TAMANHO_AMOSTRA} musicas (estratificado por genero)...")
    amostra = amostrar_por_genero(musicas, TAMANHO_AMOSTRA, SEED)
    print(f"    {len(amostra)} musicas selecionadas.")
    generos = Counter(m["track_genre"] for m in amostra)
    print(f"    Generos representados: {len(generos)}")

    print(f"\n[3] Normalizando atributos...")
    normalizar_atributos(amostra)

    print(f"\n[4] Construindo arestas (K={K_VIZINHOS} vizinhos mais proximos)...")
    arestas = construir_arestas_knn(amostra, K_VIZINHOS)
    print(f"    {len(arestas)} arestas criadas.")

    print(f"\n[5] Calculando distribuicao de graus...")
    graus = calcular_distribuicao_graus(arestas, amostra)

    print(f"\n[6] Salvando arquivos...")
    salvar_nos_csv(amostra, str(out_dir / "musicas_nos.csv"))
    print(f"    musicas_nos.csv salvo.")
    salvar_arestas_csv(arestas, str(out_dir / "adjacencias_musicas.csv"))
    print(f"    adjacencias_musicas.csv salvo.")
    salvar_descricao(amostra, arestas, graus, str(out_dir / "descricao_dataset.txt"))

    frontend_json = base_dir / "frontend" / "src" / "data" / "graph.json"
    if frontend_json.parent.exists():
        gerar_graph_json(amostra, arestas, graus, str(frontend_json))

    print(f"\n{'=' * 55}")
    print(f"RESUMO DO GRAFO")
    print(f"{'=' * 55}")
    print(f"  |V| = {len(amostra)}")
    print(f"  |E| = {len(arestas)}")
    print(f"  Tipo: Nao dirigido, Ponderado")
    print(f"  Grau min={min(graus.values())}  max={max(graus.values())}  "
          f"medio={sum(graus.values())/len(graus):.2f}")
    print(f"\nArquivos salvos em: {out_dir}")
    print("Concluido!")


if __name__ == "__main__":
    main()
