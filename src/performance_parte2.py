import os
import sys
import json
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_musicas, ler_adjacencias_musicas
from graphs.algorithms import bfs, dfs, dijkstra, bellman_ford, dfs_componentes_conexos

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data" / "dataset_parte2"
OUT_DIR    = BASE_DIR / "out"
REPORT_OUT = OUT_DIR / "parte2_report.json"

NOS_CSV    = DATA_DIR / "musicas_nos.csv"
ADJ_CSV    = DATA_DIR / "adjacencias_musicas.csv"

MEDIR_MEMORIA = True


def medir(fn, *args, **kwargs):
    """
    Executa fn(*args, **kwargs) e retorna:
      resultado, tempo_ms, memoria_kb (ou None se desativado)
    """
    if MEDIR_MEMORIA:
        tracemalloc.start()

    inicio = time.perf_counter()
    resultado = fn(*args, **kwargs)
    fim = time.perf_counter()

    tempo_ms = round((fim - inicio) * 1000, 4)

    if MEDIR_MEMORIA:
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memoria_kb = round(pico / 1024, 2)
    else:
        memoria_kb = None

    return resultado, tempo_ms, memoria_kb


def entrada_para_str(grafo):
    n = len(grafo.get_nos())
    m = sum(len(v) for v in grafo.adj_list.values()) // 2
    return f"|V|={n}, |E|={m}"


def carregar_grafo():
    print("Carregando grafo Spotify...")
    grafo = ler_musicas(str(NOS_CSV))
    ler_adjacencias_musicas(grafo, str(ADJ_CSV))
    nos = grafo.get_nos()
    print(f"  {grafo}  — {len(nos)} vértices disponíveis")
    return grafo, nos


def tarefa_carregamento(nos_csv, adj_csv):
    """Leitura completa dos CSVs e construção do grafo."""
    g = ler_musicas(str(nos_csv))
    ler_adjacencias_musicas(g, str(adj_csv))
    return g


def tarefa_bfs(grafo, origem):
    return bfs(grafo, origem)


def tarefa_dfs(grafo, origem):
    return dfs(grafo, origem)


def tarefa_dijkstra(grafo, origem):
    return dijkstra(grafo, origem)


def tarefa_bellman_ford(grafo, origem):
    return bellman_ford(grafo, origem)


def tarefa_componentes(grafo):
    return dfs_componentes_conexos(grafo)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 0. Carregamento (medido) ──────────────
    print("\n[0] Medindo carregamento do grafo...")
    _, t_load, m_load = medir(tarefa_carregamento, NOS_CSV, ADJ_CSV)
    grafo, nos = carregar_grafo()
    origem = nos[0]  # primeiro nó como origem padrão
    desc_entrada = entrada_para_str(grafo)

    print(f"    tempo: {t_load} ms  |  memória pico: {m_load} KB")

    # bfs
    print("\n[1] Medindo BFS...")
    _, t_bfs, m_bfs = medir(tarefa_bfs, grafo, origem)
    print(f"    origem: {origem}")
    print(f"    tempo: {t_bfs} ms  |  memória pico: {m_bfs} KB")

    # dfs
    print("\n[2] Medindo DFS...")
    _, t_dfs, m_dfs = medir(tarefa_dfs, grafo, origem)
    print(f"    origem: {origem}")
    print(f"    tempo: {t_dfs} ms  |  memória pico: {m_dfs} KB")

    #- dijkstra
    print("\n[3] Medindo Dijkstra...")
    _, t_dij, m_dij = medir(tarefa_dijkstra, grafo, origem)
    print(f"    origem: {origem}")
    print(f"    tempo: {t_dij} ms  |  memória pico: {m_dij} KB")

    # bellman-ford
    print("\n[4] Medindo Bellman-Ford...")
    _, t_bf, m_bf = medir(tarefa_bellman_ford, grafo, origem)
    print(f"    origem: {origem}")
    print(f"    tempo: {t_bf} ms  |  memória pico: {m_bf} KB")

    # os componentes conexos
    print("\n[5] Medindo Componentes Conexos (DFS global)...")
    resultado_comp, t_comp, m_comp = medir(tarefa_componentes, grafo)
    num_comp = len(resultado_comp)
    print(f"    componentes encontrados: {num_comp}")
    print(f"    tempo: {t_comp} ms  |  memória pico: {m_comp} KB")

    #  Monta relatório 
    relatorio = {
        "descricao": (
            "Métricas de desempenho dos algoritmos de grafos aplicados "
            "ao grafo de similaridade musical Spotify (Parte 2)."
        ),
        "grafo": {
            "dataset": "Spotify Tracks — dataset_parte2",
            "vertices": len(nos),
            "arestas": sum(len(v) for v in grafo.adj_list.values()) // 2,
            "tipo": "não dirigido, ponderado",
        },
        "medicoes": [
            {
                "tarefa": "Carregamento do grafo",
                "algoritmo": "leitura de CSV + construção da lista de adjacência",
                "entrada": f"musicas_nos.csv + adjacencias_musicas.csv ({desc_entrada})",
                "tempo_ms": t_load,
                "memoria_pico_kb": m_load,
                "observacoes": "Inclui leitura de arquivo e inserção de todos os nós e arestas.",
            },
            {
                "tarefa": "BFS (Busca em Largura)",
                "algoritmo": "BFS iterativo com fila (deque)",
                "entrada": desc_entrada,
                "origem": origem,
                "tempo_ms": t_bfs,
                "memoria_pico_kb": m_bfs,
                "complexidade_teorica": "O(V + E)",
                "observacoes": "Percorre todo o componente conexo a partir da origem.",
            },
            {
                "tarefa": "DFS (Busca em Profundidade)",
                "algoritmo": "DFS recursivo com coloração BRANCO/CINZA/PRETO",
                "entrada": desc_entrada,
                "origem": origem,
                "tempo_ms": t_dfs,
                "memoria_pico_kb": m_dfs,
                "complexidade_teorica": "O(V + E)",
                "observacoes": "Percorre todos os vértices do grafo (não apenas um componente).",
            },
            {
                "tarefa": "Dijkstra (caminho mínimo)",
                "algoritmo": "Dijkstra com heap binário (heapq)",
                "entrada": desc_entrada,
                "origem": origem,
                "tempo_ms": t_dij,
                "memoria_pico_kb": m_dij,
                "complexidade_teorica": "O((V + E) log V)",
                "observacoes": "Calcula distâncias mínimas de origem para todos os demais vértices.",
            },
            {
                "tarefa": "Bellman-Ford (caminho mínimo)",
                "algoritmo": "Bellman-Ford iterativo (V-1 relaxamentos)",
                "entrada": desc_entrada,
                "origem": origem,
                "tempo_ms": t_bf,
                "memoria_pico_kb": m_bf,
                "complexidade_teorica": "O(V * E)",
                "observacoes": (
                    "Aceita pesos negativos e detecta ciclos negativos. "
                    "Neste dataset os pesos são distâncias euclidianas (≥ 0), "
                    "portanto Dijkstra e Bellman-Ford produzem os mesmos caminhos."
                ),
            },
            {
                "tarefa": "Componentes Conexos",
                "algoritmo": "DFS global iterativo",
                "entrada": desc_entrada,
                "componentes_encontrados": num_comp,
                "tempo_ms": t_comp,
                "memoria_pico_kb": m_comp,
                "complexidade_teorica": "O(V + E)",
                "observacoes": (
                    f"Identifica todos os componentes conexos do grafo. "
                    f"Resultado: {num_comp} componente(s)."
                ),
            },
        ],
        "resumo_comparativo": {
            "mais_rapido_ms": min(t_bfs, t_dfs, t_dij, t_bf, t_comp),
            "mais_lento_ms":  max(t_bfs, t_dfs, t_dij, t_bf, t_comp),
            "ordem_por_tempo_crescente": sorted(
                [
                    ("BFS",                t_bfs),
                    ("DFS",                t_dfs),
                    ("Dijkstra",           t_dij),
                    ("Bellman-Ford",       t_bf),
                    ("Componentes Conexos",t_comp),
                ],
                key=lambda x: x[1],
            ),
        },
        "metadados": {
            "medicao_de_memoria": MEDIR_MEMORIA,
            "unidade_tempo": "milissegundos (ms)",
            "unidade_memoria": "kilobytes (KB) — pico alocado durante execução",
            "ferramenta_memoria": "tracemalloc (stdlib Python)",
            "nota": (
                "Os tempos podem variar entre execuções por fatores do SO "
                "(cache, agendador). Recomenda-se repetir e tirar a média para benchmarks rigorosos."
            ),
        },
    }

    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Relatório salvo em: {REPORT_OUT}")
    print("\n══════════════════════════════════════════════")
    print("  RESUMO — TEMPO DE EXECUÇÃO (ms)")
    print("══════════════════════════════════════════════")
    print(f"  {'Tarefa':<30} {'Tempo (ms)':>12}  {'Mem pico (KB)':>14}")
    print(f"  {'-'*30} {'-'*12}  {'-'*14}")
    for m in relatorio["medicoes"]:
        mem = str(m["memoria_pico_kb"]) if m["memoria_pico_kb"] is not None else "—"
        print(f"  {m['tarefa']:<30} {m['tempo_ms']:>12.4f}  {mem:>14}")
    print("══════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()