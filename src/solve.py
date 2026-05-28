"""
Parte 2 — Execução de BFS e DFS no grafo de similaridade musical Spotify.

Carrega o dataset_parte2, roda BFS e DFS a partir de 3 fontes distintas
(critério obrigatório: BFS/DFS executados a partir de pelo menos 3 fontes).

Arquivos gerados:
  out/bfs_dataset2.json      — BFS a partir da Fonte 1 (referência principal)
  out/dfs_dataset2.json      — DFS a partir da Fonte 1 (referência principal)
  out/bfs_dataset2_f2.json   — BFS a partir da Fonte 2
  out/dfs_dataset2_f2.json   — DFS a partir da Fonte 2
  out/bfs_dataset2_f3.json   — BFS a partir da Fonte 3
  out/dfs_dataset2_f3.json   — DFS a partir da Fonte 3

Uso:
    python -m src.solve                        # roda as 3 fontes padrão
    python -m src.solve --source <track_id>    # roda apenas 1 fonte específica
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_musicas, ler_adjacencias_musicas
from graphs.algorithms import bfs, bfs_por_niveis, dfs

# Caminhos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOS_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "musicas_nos.csv")
ADJ_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "adjacencias_musicas.csv")
OUT_DIR  = os.path.join(BASE_DIR, "out")

# Três fontes distintas — critério obrigatório (≥ 3 origens para BFS/DFS)
FONTES = [
    "7g96GMqMFfkrzEvDwSIWzQ",   # Fonte 1: "Failing, Flailing" – Streetlight Manifesto (ska)
    "2l2zYplvdjpRDEAmoHKX0t",   # Fonte 2: "Just Can't Get Enough" (happy) — região central do grafo
    "3D4J0o9w44QKFrBrYrSVJY",   # Fonte 3: "What Comes Next?" (show-tunes) — região final do grafo
]

ORIGEM_PADRAO = FONTES[0]


# Helpers

def _salvar_json(dados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  Salvo: {caminho}")


def _nome_musica(grafo, track_id):
    """Retorna 'Nome – Artista (gênero)' ou só o track_id se não encontrado."""
    attrs = grafo.get_atributos_no(track_id)
    if not attrs:
        return track_id
    nome    = attrs.get("track_name", "")
    artista = attrs.get("artists", "")
    genero  = attrs.get("track_genre", "")
    return f"{nome} – {artista} ({genero})" if nome else track_id


# Execução BFS

def executar_bfs(grafo, origem, nome_arquivo, out_dir):
    """Executa BFS a partir de 'origem' e salva o resultado em 'nome_arquivo'."""
    print(f"\n[BFS] Origem: {origem}")
    print(f"      Música : {_nome_musica(grafo, origem)}")

    t0 = time.perf_counter()
    ordem_visita, niveis, predecessores, arestas_tipo = bfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    camadas = bfs_por_niveis(grafo, origem)

    tipos_contagem = {}
    vistas = set()
    for u, v, tipo in arestas_tipo:
        chave = (min(u, v), max(u, v))
        if chave not in vistas:
            vistas.add(chave)
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

    print(f"      Nós visitados   : {len(ordem_visita)}")
    print(f"      Nível máximo    : {max(niveis.values())}")
    print(f"      Camadas (qtd)   : {len(camadas)}")
    print(f"      Arestas tipo    : {tipos_contagem}")
    print(f"      Tempo           : {elapsed * 1000:.4f} ms")

    resultado = {
        "algoritmo"    : "BFS",
        "dataset"      : "Spotify Tracks — dataset_parte2",
        "origem"       : origem,
        "musica_origem": _nome_musica(grafo, origem),
        "tempo_ms"     : round(elapsed * 1000, 4),
        "nos_visitados": len(ordem_visita),
        "nivel_maximo" : max(niveis.values()),
        "ordem_visita" : ordem_visita,
        "niveis"       : niveis,
        "camadas"      : camadas,
        "arestas_tipo" : tipos_contagem,
        "complexidade" : "O(V + E)",
    }

    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
    return resultado


# Execução DFS

def executar_dfs(grafo, origem, nome_arquivo, out_dir):
    """Executa DFS a partir de 'origem' e salva o resultado em 'nome_arquivo'."""
    print(f"\n[DFS] Origem: {origem}")
    print(f"      Música : {_nome_musica(grafo, origem)}")

    t0 = time.perf_counter()
    ordem_visita, predecessores, t_entrada, t_saida, arestas_tipo, tem_ciclo = dfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    tipos_contagem = {}
    vistas = set()
    for u, v, tipo in arestas_tipo:
        chave = (min(u, v), max(u, v))
        if chave not in vistas:
            vistas.add(chave)
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

    print(f"      Nós visitados   : {len(ordem_visita)}")
    print(f"      Ciclo detectado : {'SIM' if tem_ciclo else 'NÃO'}")
    print(f"      Arestas tipo    : {tipos_contagem}")
    print(f"      Tempo           : {elapsed * 1000:.4f} ms")

    resultado = {
        "algoritmo"    : "DFS",
        "dataset"      : "Spotify Tracks — dataset_parte2",
        "origem"       : origem,
        "musica_origem": _nome_musica(grafo, origem),
        "tempo_ms"     : round(elapsed * 1000, 4),
        "nos_visitados": len(ordem_visita),
        "tem_ciclo"    : tem_ciclo,
        "ordem_visita" : ordem_visita,
        "arestas_tipo" : tipos_contagem,
        "tempo_entrada": t_entrada,
        "tempo_saida"  : t_saida,
        "complexidade" : "O(V + E)",
    }

    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
    return resultado


# Main

def parse_args():
    parser = argparse.ArgumentParser(
        prog="python -m src.solve",
        description=(
            "Parte 2 — Executa BFS e DFS no grafo de similaridade musical Spotify. "
            "Por padrão executa a partir de 3 fontes distintas (critério obrigatório)."
        ),
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Track ID de origem para execução única (omitir = rodar as 3 fontes padrão)",
    )
    parser.add_argument(
        "--out",
        default=OUT_DIR,
        help=f"Pasta de saída (padrão: {OUT_DIR})",
    )
    return parser.parse_args()


def main():
    args    = parse_args()
    out_dir = os.path.abspath(args.out)

    print("=" * 60)
    print("  PARTE 2 — BFS e DFS · Grafo de Similaridade Musical")
    print("=" * 60)

    print("\n[0] Carregando grafo Spotify...")
    if not os.path.exists(NOS_CSV):
        print(f"Erro: arquivo não encontrado: {NOS_CSV}")
        sys.exit(1)
    if not os.path.exists(ADJ_CSV):
        print(f"Erro: arquivo não encontrado: {ADJ_CSV}")
        sys.exit(1)

    grafo = ler_musicas(NOS_CSV)
    ler_adjacencias_musicas(grafo, ADJ_CSV)

    nos   = grafo.get_nos()
    n_nos = len(nos)
    n_are = sum(len(v) for v in grafo.adj_list.values()) // 2
    print(f"     Grafo carregado: |V|={n_nos}  |E|={n_are}  (não dirigido, ponderado)")

    if args.source is not None:
        origem = args.source
        if origem not in grafo.adj_list:
            print(f"\nErro: nó de origem '{origem}' não existe no grafo.")
            print(f"Exemplo de nó válido: {nos[0]}")
            sys.exit(1)
        executar_bfs(grafo, origem, "bfs_dataset2.json", out_dir)
        executar_dfs(grafo, origem, "dfs_dataset2.json", out_dir)
        print("\n" + "=" * 60)
        print("  Resultados salvos em:", out_dir)
        print("    · bfs_dataset2.json")
        print("    · dfs_dataset2.json")
        print("=" * 60)
        return

    sufixos_bfs = ["bfs_dataset2.json", "bfs_dataset2_f2.json", "bfs_dataset2_f3.json"]
    sufixos_dfs = ["dfs_dataset2.json", "dfs_dataset2_f2.json", "dfs_dataset2_f3.json"]

    arquivos_gerados = []
    for i, origem in enumerate(FONTES):
        if origem not in grafo.adj_list:
            print(f"\nAviso: fonte {i+1} '{origem}' não encontrada no grafo — ignorando.")
            continue

        print(f"\n{'='*60}")
        print(f"  Fonte {i+1} de {len(FONTES)}: {_nome_musica(grafo, origem)}")
        print(f"{'='*60}")

        executar_bfs(grafo, origem, sufixos_bfs[i], out_dir)
        executar_dfs(grafo, origem, sufixos_dfs[i], out_dir)

        arquivos_gerados += [sufixos_bfs[i], sufixos_dfs[i]]

    print("\n" + "=" * 60)
    print("  Resultados salvos em:", out_dir)
    for arq in arquivos_gerados:
        print(f"    · {arq}")
    print("=" * 60)


if __name__ == "__main__":
    main()
