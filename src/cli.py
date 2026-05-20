import argparse
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias #importando de dentro do projeto esses arquivo
from graphs.algorithms import ( 
    bfs, bfs_por_niveis,
    dfs,
    dijkstra_caminho,
)

def _garantir_pasta(caminho):
    os.makedirs(caminho, exist_ok=True)


def _salvar_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {caminho}")


def _salvar_csv(linhas, campos, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)
    print(f"Salvo: {caminho}")

#BFS
def executar_bfs(grafo, origem, out_dir):
    print(f"BFS a partir de: {origem}")

    t0 = time.perf_counter()
    ordem_visita, niveis, predecessores, arestas_tipo = bfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    camadas = bfs_por_niveis(grafo, origem)

    print(f"\nOrdem de visita ({len(ordem_visita)} nós):")
    print("  " + " => ".join(ordem_visita))

    print(f"\nCamadas BFS:")
    for i, camada in enumerate(camadas):
        print(f"Nível {i}: {camada}")

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
        "ordem_visita" : ordem_visita,
        "niveis"       : niveis,
        "camadas"      : camadas,
        "arestas_tipo" : tipos_contagem,
    }
    _salvar_json(resultado, os.path.join(out_dir, f"bfs_{origem}.json"))

#DFS
def executar_dfs(grafo, origem, out_dir):
    print(f"  DFS a partir de: {origem}")

    t0 = time.perf_counter()
    ordem_visita, predecessores, t_entrada, t_saida, arestas_tipo, tem_ciclo = dfs(grafo, origem)
    elapsed = time.perf_counter() - t0

    print(f"\nOrdem de visita ({len(ordem_visita)} nós):")
    print("  " + " => ".join(ordem_visita))

    #classificando para grafo n direcional 
    tipos_contagem = {}
    vistas = set()
    for u, v, tipo in arestas_tipo:
        chave = (min(u, v), max(u, v))
        if chave not in vistas:
            vistas.add(chave)
            tipos_contagem[tipo] = tipos_contagem.get(tipo, 0) + 1

    print(f"\nClassificação de arestas: {tipos_contagem}")
    print(f"Ciclo detectado? {'SIM' if tem_ciclo else 'NÃO'}")
    print(f"\nTempos de entrada/saída:")
    for no in ordem_visita:
        print(f"{no}: entrada={t_entrada.get(no,'?')} / saída={t_saida.get(no,'?')}")

    print(f"\nTempo de execução: {elapsed*1000:.3f} ms")

    resultado = {
        "algoritmo"    : "DFS",
        "origem"       : origem,
        "tempo_ms"     : round(elapsed * 1000, 4),
        "nos_visitados": len(ordem_visita),
        "ordem_visita" : ordem_visita,
        "tem_ciclo"    : tem_ciclo,
        "arestas_tipo" : tipos_contagem,
        "tempo_entrada": t_entrada,
        "tempo_saida"  : t_saida,
    }
    _salvar_json(resultado, os.path.join(out_dir, f"dfs_{origem}.json"))

#Dijkstra
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

def parse_args():
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Projeto Grafos — Rede de Aeroportos do Brasil",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--dataset",
        required=True,
        help="Caminho para aeroportos_data.csv (ou pasta com dataset Parte 2)",
    )
    parser.add_argument(
        "--alg",
        required=True,
        choices=["BFS", "DFS", "DIJKSTRA"],
        help="Algoritmo a executar: BFS | DFS | DIJKSTRA",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Nó de origem (ex: REC)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Nó de destino — obrigatório para DIJKSTRA (ex: POA)",
    )
    parser.add_argument(
        "--out",
        default="./out/",
        help="Pasta de saída (padrão: ./out/)",
    )
    parser.add_argument(
        "--adj",
        default=None,
        help="Caminho para adjacencias_aeroportos.csv\n"
             "(padrão: mesma pasta do dataset)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    dataset_path = os.path.abspath(args.dataset)
    out_dir      = os.path.abspath(args.out)
    _garantir_pasta(out_dir)

    if args.adj:
        adj_path = os.path.abspath(args.adj)
    else:
        data_dir = (
            os.path.dirname(dataset_path)
            if os.path.isfile(dataset_path)
            else dataset_path
        )
        adj_path = os.path.join(data_dir, "adjacencias_aeroportos.csv")

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

    print(f"\n{grafo}")
    print(f"Nós: {grafo.get_nos()}")

    source = args.source.strip().upper()
    if source not in grafo.get_nos():
        print(f"\nErro: nó de origem {source} não existe no grafo.")
        print(f"Nós disponíveis: {sorted(grafo.get_nos())}")
        sys.exit(1)

    alg = args.alg.upper()

    if alg == "BFS":
        executar_bfs(grafo, source, out_dir)

    elif alg == "DFS":
        executar_dfs(grafo, source, out_dir)

    elif alg == "DIJKSTRA":
        if not args.target:
            print("Erro: --target é obrigatório para o algoritmo DIJKSTRA.")
            sys.exit(1)
        target = args.target.strip().upper()
        executar_dijkstra(grafo, source, target, out_dir)

    print(f"\nConcluído. Os resultados foram salvos em: {out_dir}")


if __name__ == "__main__":
    main()
