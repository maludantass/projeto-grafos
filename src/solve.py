import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_musicas, ler_adjacencias_musicas
from graphs.algorithms import bfs, bfs_por_niveis, dfs, dijkstra, dijkstra_caminho, bellman_ford, bellman_ford_caminho

# Caminhos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOS_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "musicas_nos.csv")
ADJ_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "adjacencias_musicas.csv")
OUT_DIR  = os.path.join(BASE_DIR, "out")

# Três fontes distintas — critério obrigatório (≥ 3 origens para BFS/DFS)
FONTES = [
    "3pyQ7RB5P8iwZMkPAeZ3ym",   # Fonte 1: "Seu Zé Que Ta Chegando - Ao Vivo" (brazil)
    "4kLyAbRTMMfmAH5Fjm3cYU",   # Fonte 2: "Eleanor - Edit" (pop)
    "1DIXPcTDzTj8ZMHt3PDt8p",   # Fonte 3: "Gangsta's Paradise" (funk)
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

# dijkstra
def executar_dijkstra_spotify(grafo, origem, destino, nome_arquivo, out_dir):
    """Executa Dijkstra entre dois nós do grafo Spotify e salva o resultado."""
    print(f"\n[DIJKSTRA] Origem : {origem}")
    print(f"           Música : {_nome_musica(grafo, origem)}")
    print(f"           Destino: {destino}")
    print(f"           Música : {_nome_musica(grafo, destino)}")

    t0 = time.perf_counter()
    custo, caminho = dijkstra_caminho(grafo, origem, destino)
    elapsed = time.perf_counter() - t0

    if caminho is None:
        print(f"      Destino inacessível a partir da origem.")
    else:
        print(f"      Caminho ({len(caminho) - 1} saltos): {' => '.join(caminho)}")
        print(f"      Custo total (distância euclidiana): {custo:.6f}")

    print(f"      Tempo: {elapsed * 1000:.4f} ms")

    resultado = {
        "algoritmo"     : "Dijkstra",
        "dataset"       : "Spotify Tracks — dataset_parte2",
        "origem"        : origem,
        "musica_origem" : _nome_musica(grafo, origem),
        "destino"       : destino,
        "musica_destino": _nome_musica(grafo, destino),
        "custo"         : round(custo, 6) if custo != float("inf") else None,
        "caminho"       : caminho,
        "saltos"        : len(caminho) - 1 if caminho else None,
        "tempo_ms"      : round(elapsed * 1000, 4),
        "complexidade"  : "O((V + E) log V)",
        "observacoes"   : (
            "Peso = distância euclidiana entre vetores de atributos musicais. "
            "Caminho mínimo = sequência de músicas mais similares entre origem e destino."
        ),
    }

    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
    return resultado


# bellman-ford
def executar_bellman_ford_spotify(grafo, origem, destino, nome_arquivo, out_dir):
    print(f"\n[BELLMAN-FORD] Origem : {origem}")
    print(f"               Música : {_nome_musica(grafo, origem)}")
    print(f"               Destino: {destino}")
    print(f"               Música : {_nome_musica(grafo, destino)}")

    t0 = time.perf_counter()
    try:
        custo, caminho = bellman_ford_caminho(grafo, origem, destino)
        ciclo_negativo = False
    except ValueError as e:
        elapsed = time.perf_counter() - t0
        print(f"      ERRO: {e}")
        resultado = {
            "algoritmo"     : "Bellman-Ford",
            "dataset"       : "Spotify Tracks — dataset_parte2",
            "origem"        : origem,
            "destino"       : destino,
            "erro"          : str(e),
            "ciclo_negativo": True,
            "tempo_ms"      : round(elapsed * 1000, 4),
        }
        _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
        return resultado

    elapsed = time.perf_counter() - t0

    if caminho is None:
        print(f"      Destino inacessível a partir da origem.")
    else:
        print(f"      Caminho ({len(caminho) - 1} saltos): {' => '.join(caminho)}")
        print(f"      Custo total (distância euclidiana): {custo:.6f}")

    print(f"      Tempo: {elapsed * 1000:.4f} ms")

    resultado = {
        "algoritmo"     : "Bellman-Ford",
        "dataset"       : "Spotify Tracks — dataset_parte2",
        "origem"        : origem,
        "musica_origem" : _nome_musica(grafo, origem),
        "destino"       : destino,
        "musica_destino": _nome_musica(grafo, destino),
        "custo"         : round(custo, 6) if custo != float("inf") else None,
        "caminho"       : caminho,
        "saltos"        : len(caminho) - 1 if caminho else None,
        "ciclo_negativo": ciclo_negativo,
        "tempo_ms"      : round(elapsed * 1000, 4),
        "complexidade"  : "O(V * E)",
        "observacoes"   : (
            "Aceita pesos negativos (não há neste dataset). "
            "Peso = distância euclidiana entre vetores de atributos musicais. "
            "Caminho mínimo = sequência de músicas mais similares entre origem e destino."
        ),
    }

    _salvar_json(resultado, os.path.join(out_dir, nome_arquivo))
    return resultado

# casos especiais bellman-ford
def _executar_bf_peso_negativo_sem_ciclo(out_dir):
    from src.graphs.graph import GrafoDirecionado
    from src.graphs.algorithms import bellman_ford_caminho, dijkstra_caminho

    g = GrafoDirecionado()
    for no in ["A", "B", "C", "D"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=5.0)
    g.adicionar_aresta("B", "C", peso=-2.0)
    g.adicionar_aresta("C", "D", peso=1.0)
    g.adicionar_aresta("B", "D", peso=4.0)

    custo_bf, caminho_bf = bellman_ford_caminho(g, "A", "D")

    try:
        custo_dij, caminho_dij = dijkstra_caminho(g, "A", "D")
        dijkstra_resultado = {"custo": custo_dij, "caminho": caminho_dij}
    except ValueError as e:
        dijkstra_resultado = {"erro": str(e)}

    print(f"Grafo direcionado: A→B(5), B→C(-2), C→D(1), B→D(4)")
    print(f"Bellman-Ford A→D: caminho={caminho_bf}, custo={custo_bf}")
    print(f"Dijkstra A→D: {dijkstra_resultado}")

    resultado = {
        "algoritmo": "Bellman-Ford",
        "tipo_caso": "peso_negativo_sem_ciclo",
        "descricao": (
            "Grafo direcionado sintético com aresta de peso negativo (B→C = -2) "
            "mas sem ciclo negativo. Bellman-Ford resolve corretamente; "
            "Dijkstra rejeita pesos negativos."
        ),
        "grafo": {
            "tipo": "direcionado",
            "arestas": [
                {"u": "A", "v": "B", "peso": 5.0},
                {"u": "B", "v": "C", "peso": -2.0},
                {"u": "C", "v": "D", "peso": 1.0},
                {"u": "B", "v": "D", "peso": 4.0},
            ],
        },
        "origem": "A",
        "destino": "D",
        "bellman_ford": {
            "custo": custo_bf,
            "caminho": caminho_bf,
            "ciclo_negativo_detectado": False,
        },
        "dijkstra": dijkstra_resultado,
        "observacao": "Caminho mínimo A→B→C→D = 5 + (-2) + 1 = 4 (melhor que A→B→D = 5 + 4 = 9)",
    }
    _salvar_json(resultado, os.path.join(out_dir, "bellman_ford_peso_negativo.json"))


def _executar_bf_ciclo_negativo(out_dir):

    from src.graphs.graph import GrafoDirecionado
    from src.graphs.algorithms import bellman_ford

    g = GrafoDirecionado()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=1.0)
    g.adicionar_aresta("B", "C", peso=-3.0)
    g.adicionar_aresta("C", "A", peso=1.0)

    print(f"      Grafo direcionado: A→B(1), B→C(-3), C→A(1)")
    print(f"      Ciclo A→B→C→A = 1 + (-3) + 1 = -1 (negativo)")

    try:
        bellman_ford(g, "A")
        ciclo_detectado = False
        mensagem_erro = None
        print(f"      ERRO: ciclo negativo não foi detectado!")
    except ValueError as e:
        ciclo_detectado = True
        mensagem_erro = str(e)
        print(f"      Ciclo negativo detectado corretamente: {e}")

    resultado = {
        "algoritmo": "Bellman-Ford",
        "tipo_caso": "ciclo_negativo",
        "descricao": (
            "Grafo direcionado sintético com ciclo negativo A→B→C→A "
            "(custo do ciclo = 1 + (-3) + 1 = -1). "
            "Bellman-Ford detecta na V-ésima iteração e lança erro."
        ),
        "grafo": {
            "tipo": "direcionado",
            "arestas": [
                {"u": "A", "v": "B", "peso": 1.0},
                {"u": "B", "v": "C", "peso": -3.0},
                {"u": "C", "v": "A", "peso": 1.0},
            ],
            "custo_do_ciclo": -1.0,
        },
        "origem": "A",
        "ciclo_negativo_detectado": ciclo_detectado,
        "mensagem_erro": mensagem_erro,
        "observacao": "Caminho mínimo não existe — ciclo negativo faz distâncias divergirem para -∞.",
    }
    _salvar_json(resultado, os.path.join(out_dir, "bellman_ford_ciclo_negativo.json"))


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

    print(f"\n{'='*60}")
    print(f"  Dijkstra — 5 pares origem/destino (pesos ≥ 0)")
    print(f"{'='*60}")

    pares_dijkstra = [
        (FONTES[0], FONTES[1]),
        (FONTES[1], FONTES[2]),
        (FONTES[0], FONTES[2]),
        (FONTES[1], FONTES[0]),
        (FONTES[2], FONTES[0]),
    ]
    sufixos_dij = [
        "dijkstra_dataset2_f1_f2.json",
        "dijkstra_dataset2_f2_f3.json",
        "dijkstra_dataset2_f1_f3.json",
        "dijkstra_dataset2_f2_f1.json",
        "dijkstra_dataset2_f3_f1.json",
    ]

    for i, (origem, destino) in enumerate(pares_dijkstra):
        if origem not in grafo.adj_list or destino not in grafo.adj_list:
            print(f"\nAviso: par {i+1} inválido — nó não encontrado no grafo.")
            continue
        executar_dijkstra_spotify(grafo, origem, destino, sufixos_dij[i], out_dir)
        arquivos_gerados.append(sufixos_dij[i])

    print(f"\n{'='*60}")
    print(f"  Bellman-Ford — dataset real + casos especiais")
    print(f"{'='*60}")

    pares_bf = [
        (FONTES[0], FONTES[1]),
        (FONTES[1], FONTES[2]),
        (FONTES[0], FONTES[2]),
    ]
    sufixos_bf = [
        "bellman_ford_dataset2_f1_f2.json",
        "bellman_ford_dataset2_f2_f3.json",
        "bellman_ford_dataset2_f1_f3.json",
    ]

    for i, (origem, destino) in enumerate(pares_bf):
        if origem not in grafo.adj_list or destino not in grafo.adj_list:
            continue
        executar_bellman_ford_spotify(grafo, origem, destino, sufixos_bf[i], out_dir)
        arquivos_gerados.append(sufixos_bf[i])

    # grafo direcionado com peso negativo sem ciclo negativo
    print(f"\n[BELLMAN-FORD — peso negativo sem ciclo (grafo direcionado sintético)]")
    _executar_bf_peso_negativo_sem_ciclo(out_dir)
    arquivos_gerados.append("bellman_ford_peso_negativo.json")

    # grafo direcionado com ciclo negativo -> detectar
    print(f"\n[BELLMAN-FORD — ciclo negativo detectado (grafo direcionado sintético)]")
    _executar_bf_ciclo_negativo(out_dir)
    arquivos_gerados.append("bellman_ford_ciclo_negativo.json")

    print("\n" + "=" * 60)
    print("  Resultados salvos em:", out_dir)
    for arq in arquivos_gerados:
        print(f"    · {arq}")
    print("=" * 60)


if __name__ == "__main__":
    main()