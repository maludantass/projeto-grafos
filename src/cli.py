import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias, ler_musicas, ler_adjacencias_musicas
from graphs.algorithms import (
    bfs, bfs_por_niveis,
    dfs,
    dijkstra_caminho,
    bellman_ford_caminho,
)


def _garantir_pasta(caminho):
    os.makedirs(caminho, exist_ok=True)


def _salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {caminho}")


def _is_parte2(dataset_path):
    # Parte 2 é sempre um diretório; Parte 1 é um arquivo CSV
    return os.path.isdir(dataset_path)


def _carregar_grafo_parte1(dataset_path, adj_path):
    print(f"Lendo aeroportos: {dataset_path}")
    try:
        grafo = ler_aeroportos(dataset_path)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {dataset_path}")
        sys.exit(1)

    print(f"Lendo adjacências: {adj_path}")
    try:
        ler_adjacencias(grafo, adj_path)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {adj_path}")
        sys.exit(1)

    return grafo


def _carregar_grafo_parte2(dataset_path, adj_path=None):
    nos_path = os.path.join(dataset_path, "musicas_nos.csv")
    if adj_path is None:
        adj_path = os.path.join(dataset_path, "adjacencias_musicas.csv")

    print(f"Lendo músicas: {nos_path}")
    try:
        grafo = ler_musicas(nos_path)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {nos_path}")
        sys.exit(1)

    print(f"Lendo adjacências: {adj_path}")
    try:
        ler_adjacencias_musicas(grafo, adj_path)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {adj_path}")
        sys.exit(1)

    return grafo


def executar_bfs(grafo, origem, out_dir):
    print(f"BFS a partir de: {origem}")

    t0 = time.perf_counter()
    ordem_visita, niveis, predecessores, arestas_tipo = bfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    camadas = bfs_por_niveis(grafo, origem)

    print(f"\nOrdem de visita ({len(ordem_visita)} nós):")
    print("  " + " => ".join(ordem_visita[:20]) + (" ..." if len(ordem_visita) > 20 else ""))

    print(f"\nCamadas BFS:")
    for i, camada in enumerate(camadas[:10]):
        print(f"  Nível {i}: {camada[:5]}{'...' if len(camada) > 5 else ''}")
    if len(camadas) > 10:
        print(f"  ... ({len(camadas)} níveis no total)")

    # Grafo não-direcionado: cada aresta aparece duas vezes em arestas_tipo (u→v e v→u)
    # Usamos o par ordenado (min, max) para contar cada aresta apenas uma vez
    tipos_contagem = {}
    vistas = set()
    for u, v, tipo in arestas_tipo:
        chave = (min(u, v), max(u, v))
        if chave not in vistas:
            vistas.add(chave)
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

    print(f"\nClassificação de arestas: {tipos_contagem}")
    print(f"\nTempo de execução: {elapsed*1000:.3f} ms")

    resultado = {
        "algoritmo"    : "BFS",
        "origem"       : origem,
        "tempo_ms"     : round(elapsed * 1000, 4),
        "nos_visitados": len(ordem_visita),
        "nivel_maximo" : max(niveis.values()) if niveis else 0,
        "num_camadas"  : len(camadas),
        "ordem_visita" : ordem_visita,
        "niveis"       : niveis,
        "camadas"      : camadas,
        "arestas_tipo" : tipos_contagem,
    }
    _salvar_json(resultado, os.path.join(out_dir, f"bfs_{origem}.json"))


def executar_dfs(grafo, origem, out_dir):
    print(f"DFS a partir de: {origem}")

    t0 = time.perf_counter()
    ordem_visita, predecessores, t_entrada, t_saida, arestas_tipo, tem_ciclo = dfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    print(f"\nOrdem de visita ({len(ordem_visita)} nós):")
    print("  " + " => ".join(ordem_visita[:20]) + (" ..." if len(ordem_visita) > 20 else ""))

    # Mesma deduplicação do BFS: evita contar a mesma aresta duas vezes
    tipos_contagem = {}
    vistas = set()
    for u, v, tipo in arestas_tipo:
        chave = (min(u, v), max(u, v))
        if chave not in vistas:
            vistas.add(chave)
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

    print(f"\nClassificação de arestas: {tipos_contagem}")
    print(f"Ciclo detectado? {'SIM' if tem_ciclo else 'NÃO'}")
    print(f"\nTempo de execução: {elapsed*1000:.3f} ms")

    resultado = {
        "algoritmo"    : "DFS",
        "origem"       : origem,
        "tempo_ms"     : round(elapsed * 1000, 4),
        "nos_visitados": len(ordem_visita),
        "tem_ciclo"    : tem_ciclo,
        "ordem_visita" : ordem_visita,
        "arestas_tipo" : tipos_contagem,
        "tempo_entrada": t_entrada,
        "tempo_saida"  : t_saida,
    }
    _salvar_json(resultado, os.path.join(out_dir, f"dfs_{origem}.json"))


def executar_dijkstra(grafo, origem, destino, out_dir):
    print(f"DIJKSTRA: {origem} => {destino}")

    if destino not in grafo.get_nos():
        print(f"\nErro: nó destino '{destino}' não foi encontrado no grafo.")
        sys.exit(1)

    t0 = time.perf_counter()
    custo, caminho = dijkstra_caminho(grafo, origem, destino)
    elapsed = time.perf_counter() - t0

    if caminho is None:
        print(f"\nDestino '{destino}' não pode ser acessado a partir de '{origem}'.")
        resultado = {
            "algoritmo": "DIJKSTRA",
            "origem"   : origem,
            "destino"  : destino,
            "custo"    : None,
            "caminho"  : None,
            "tempo_ms" : round(elapsed * 1000, 4),
        }
    else:
        print(f"\nCaminho encontrado: {' => '.join(caminho)}")
        print(f"Custo total: {custo}")
        print(f"Saltos: {len(caminho) - 1}")
        print(f"Tempo de execução: {elapsed*1000:.3f} ms")
        resultado = {
            "algoritmo": "DIJKSTRA",
            "origem"   : origem,
            "destino"  : destino,
            "custo"    : round(custo, 4),
            "caminho"  : caminho,
            "saltos"   : len(caminho) - 1,
            "tempo_ms" : round(elapsed * 1000, 4),
        }

    nome_arquivo = f"dijkstra_{origem}_{destino}.json"
    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))


def executar_bellman_ford(grafo, origem, destino, out_dir):
    print(f"BELLMAN-FORD: {origem} => {destino}")

    if destino not in grafo.get_nos():
        print(f"\nErro: nó destino '{destino}' não foi encontrado no grafo.")
        sys.exit(1)

    t0 = time.perf_counter()
    try:
        custo, caminho = bellman_ford_caminho(grafo, origem, destino)
        elapsed = time.perf_counter() - t0
        ciclo_negativo = False
    except ValueError as e:
        elapsed = time.perf_counter() - t0
        print(f"\nDetectado: {e}")
        resultado = {
            "algoritmo"     : "BELLMAN_FORD",
            "origem"        : origem,
            "destino"       : destino,
            "erro"          : str(e),
            "ciclo_negativo": True,
            "tempo_ms"      : round(elapsed * 1000, 4),
        }
        nome_arquivo = f"bellman_ford_{origem}_{destino}.json"
        _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
        return

    if caminho is None:
        print(f"\nDestino '{destino}' não pode ser acessado a partir de '{origem}'.")
        resultado = {
            "algoritmo"     : "BELLMAN_FORD",
            "origem"        : origem,
            "destino"       : destino,
            "custo"         : None,
            "caminho"       : None,
            "ciclo_negativo": False,
            "tempo_ms"      : round(elapsed * 1000, 4),
        }
    else:
        print(f"\nCaminho encontrado: {' => '.join(caminho)}")
        print(f"Custo total: {custo}")
        print(f"Saltos: {len(caminho) - 1}")
        print(f"Tempo de execução: {elapsed*1000:.3f} ms")
        resultado = {
            "algoritmo"     : "BELLMAN_FORD",
            "origem"        : origem,
            "destino"       : destino,
            "custo"         : round(custo, 4),
            "caminho"       : caminho,
            "saltos"        : len(caminho) - 1,
            "ciclo_negativo": False,
            "tempo_ms"      : round(elapsed * 1000, 4),
        }

    nome_arquivo = f"bellman_ford_{origem}_{destino}.json"
    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))


def parse_args():
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Projeto Grafos — Rede de Aeroportos (Parte 1) e Dataset Spotify (Parte 2)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help=(
            "Caminho para aeroportos_data.csv (Parte 1)\n"
            "ou pasta dataset_parte2/ (Parte 2)"
        ),
    )
    parser.add_argument(
        "--alg",
        required=True,
        choices=["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"],
        help="Algoritmo a executar: BFS | DFS | DIJKSTRA | BELLMAN_FORD",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Nó de origem (ex: REC para Parte 1; track ID para Parte 2)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Nó de destino — obrigatório para DIJKSTRA e BELLMAN_FORD",
    )
    parser.add_argument(
        "--out",
        default="./out/",
        help="Pasta de saída (padrão: ./out/)",
    )
    parser.add_argument(
        "--adj",
        default=None,
        help=(
            "Caminho para o CSV de adjacências\n"
            "(padrão Parte 1: adjacencias_aeroportos.csv na mesma pasta;\n"
            " padrão Parte 2: adjacencias_musicas.csv dentro do diretório)"
        ),
    )

    return parser.parse_args()


def main():
    args = parse_args()

    dataset_path = os.path.abspath(args.dataset)
    out_dir      = os.path.abspath(args.out)
    _garantir_pasta(out_dir)

    parte2 = _is_parte2(dataset_path)

    if parte2:
        adj_path = os.path.abspath(args.adj) if args.adj else None
        grafo = _carregar_grafo_parte2(dataset_path, adj_path)
        source = args.source.strip()  # track IDs são case-sensitive
    else:
        if args.adj:
            adj_path = os.path.abspath(args.adj)
        else:
            data_dir = os.path.dirname(dataset_path)
            adj_path = os.path.join(data_dir, "adjacencias_aeroportos.csv")
        grafo = _carregar_grafo_parte1(dataset_path, adj_path)
        source = args.source.strip().upper()  # códigos IATA sempre em maiúsculas

    print(f"\n{grafo}")

    if source not in grafo.get_nos():
        nos_disponiveis = sorted(grafo.get_nos())
        print(f"\nErro: nó de origem '{source}' não existe no grafo.")
        print(f"Exemplo de nó válido: {nos_disponiveis[0]}")
        sys.exit(1)

    alg = args.alg.upper()

    if alg == "BFS":
        executar_bfs(grafo, source, out_dir)

    elif alg == "DFS":
        executar_dfs(grafo, source, out_dir)

    elif alg == "DIJKSTRA":
        if not args.target:
            print("Erro: --target é obrigatório para DIJKSTRA.")
            sys.exit(1)
        target = args.target.strip() if parte2 else args.target.strip().upper()
        executar_dijkstra(grafo, source, target, out_dir)

    elif alg == "BELLMAN_FORD":
        if not args.target:
            print("Erro: --target é obrigatório para BELLMAN_FORD.")
            sys.exit(1)
        target = args.target.strip() if parte2 else args.target.strip().upper()
        executar_bellman_ford(grafo, source, target, out_dir)

    print(f"\nConcluído. Resultados salvos em: {out_dir}")


if __name__ == "__main__":
    main()
