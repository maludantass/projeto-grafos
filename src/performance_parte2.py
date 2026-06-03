import os
import sys
import json
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_musicas, ler_adjacencias_musicas
from graphs.graph import GrafoDirecionado
from graphs.algorithms import bfs, dfs, dijkstra, bellman_ford, dfs_componentes_conexos

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data" / "dataset_parte2"
OUT_DIR    = BASE_DIR / "out"
REPORT_OUT = OUT_DIR / "parte2_report.json"

NOS_CSV = DATA_DIR / "musicas_nos.csv"
ADJ_CSV = DATA_DIR / "adjacencias_musicas.csv"

N_RUNS = 5  # número de repetições para calcular a média dos tempos

# Mesmas 3 fontes usadas em solve.py (critério obrigatório: ≥ 3 origens)
FONTES = [
    ("3pyQ7RB5P8iwZMkPAeZ3ym", "Seu Zé Que Ta Chegando - Ao Vivo (brazil)"),
    ("4kLyAbRTMMfmAH5Fjm3cYU", "Eleanor - Edit (pop)"),
    ("1DIXPcTDzTj8ZMHt3PDt8p", "Gangsta's Paradise (funk)"),
]


def _medir(fn, *args, **kwargs):
    """Executa fn N_RUNS vezes e retorna (resultado, tempo_medio_ms, tempo_min_ms, memoria_pico_kb)."""
    tempos = []
    resultado = None

    tracemalloc.start()
    for _ in range(N_RUNS):
        t0 = time.perf_counter()
        resultado = fn(*args, **kwargs)
        tempos.append((time.perf_counter() - t0) * 1000)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return (
        resultado,
        round(sum(tempos) / len(tempos), 4),
        round(min(tempos), 4),
        round(pico / 1024, 2),
    )


def _medir_unico(fn, *args, **kwargs):
    # Bellman-Ford é O(V*E); repetir N_RUNS vezes seria muito lento no dataset real
    tracemalloc.start()
    t0 = time.perf_counter()
    resultado = fn(*args, **kwargs)
    tempo_ms = round((time.perf_counter() - t0) * 1000, 4)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, tempo_ms, round(pico / 1024, 2)


def carregar_grafo():
    g = ler_musicas(str(NOS_CSV))
    ler_adjacencias_musicas(g, str(ADJ_CSV))
    return g


def _benchmark_bf_negativo_sem_ciclo():
    # Grafo sintético para demonstrar que Bellman-Ford lida com peso negativo
    # sem ciclo negativo — Dijkstra rejeitaria a aresta B→C(-2)
    g = GrafoDirecionado()
    for no in ["A", "B", "C", "D"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=5.0)
    g.adicionar_aresta("B", "C", peso=-2.0)
    g.adicionar_aresta("C", "D", peso=1.0)
    g.adicionar_aresta("B", "D", peso=4.0)

    t0 = time.perf_counter()
    dists, preds = bellman_ford(g, "A")
    tempo_ms = round((time.perf_counter() - t0) * 1000, 4)

    from graphs.algorithms import _reconstruir_caminho
    caminho = _reconstruir_caminho(preds, "A", "D")
    return {
        "tipo_caso": "peso_negativo_sem_ciclo",
        "descricao": "Grafo direcionado sintético: A→B(5), B→C(-2), C→D(1), B→D(4)",
        "origem": "A", "destino": "D",
        "custo": dists["D"],
        "caminho": caminho,
        "ciclo_negativo_detectado": False,
        "tempo_ms": tempo_ms,
        "observacao": "A→B→C→D = 4 (melhor que A→B→D = 9). Dijkstra rejeitaria o peso negativo.",
    }


def _benchmark_bf_ciclo_negativo():
    # Grafo sintético com ciclo A→B→C→A de custo -1; espera-se ValueError
    g = GrafoDirecionado()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=1.0)
    g.adicionar_aresta("B", "C", peso=-3.0)
    g.adicionar_aresta("C", "A", peso=1.0)

    t0 = time.perf_counter()
    try:
        bellman_ford(g, "A")
        ciclo_detectado = False
        mensagem = None
    except ValueError as e:
        ciclo_detectado = True
        mensagem = str(e)
    tempo_ms = round((time.perf_counter() - t0) * 1000, 4)

    return {
        "tipo_caso": "ciclo_negativo",
        "descricao": "Grafo direcionado sintético: A→B(1), B→C(-3), C→A(1)",
        "custo_do_ciclo": -1.0,
        "ciclo_negativo_detectado": ciclo_detectado,
        "mensagem_erro": mensagem,
        "tempo_ms": tempo_ms,
        "observacao": "Ciclo A→B→C→A = -1. Caminho mínimo não existe (distâncias → -∞).",
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  BENCHMARK PARTE 2 — Algoritmos de Grafos")
    print(f"  (cada algoritmo executado {N_RUNS}× para média estável)")
    print("=" * 60)

    print("\n[0] Carregando grafo...")
    _, t_load, t_load_min, m_load = _medir(carregar_grafo)
    grafo = carregar_grafo()
    nos = grafo.get_nos()
    n_v = len(nos)
    n_e = sum(len(v) for v in grafo.adj_list.values()) // 2
    origem = nos[0]
    print(f"    |V|={n_v}  |E|={n_e}  origem padrão: {origem}")
    print(f"    tempo médio: {t_load} ms  |  mín: {t_load_min} ms  |  mem pico: {m_load} KB")

    # BFS — 3 fontes distintas (critério obrigatório)
    medicoes_bfs = []
    for idx, (fonte_id, fonte_nome) in enumerate(FONTES, 1):
        if fonte_id not in grafo.adj_list:
            print(f"\n[BFS {idx}] Fonte '{fonte_id}' não encontrada — ignorando.")
            continue
        print(f"\n[{idx}] BFS (fonte {idx}/3): {fonte_nome}...")
        resultado_bfs, t_bfs_f, t_bfs_min_f, m_bfs_f = _medir(bfs, grafo, fonte_id)
        ordem_bfs, niveis_bfs, _, _ = resultado_bfs
        print(f"    nós visitados: {len(ordem_bfs)}  |  nível máx: {max(niveis_bfs.values())}  |  tempo médio: {t_bfs_f} ms")
        medicoes_bfs.append({
            "tarefa": f"BFS fonte {idx} — {fonte_nome}",
            "algoritmo": "BFS iterativo com fila (deque)",
            "origem": fonte_id,
            "musica_origem": fonte_nome,
            "n_runs": N_RUNS,
            "nos_visitados": len(ordem_bfs),
            "nivel_maximo": max(niveis_bfs.values()),
            "tempo_medio_ms": t_bfs_f,
            "tempo_min_ms": t_bfs_min_f,
            "memoria_pico_kb": m_bfs_f,
            "complexidade_teorica": "O(V + E)",
            "observacoes": "Percorre todo o componente conexo a partir da origem.",
        })
    t_bfs     = medicoes_bfs[0]["tempo_medio_ms"] if medicoes_bfs else 0
    t_bfs_min = medicoes_bfs[0]["tempo_min_ms"]   if medicoes_bfs else 0

    # DFS — 3 fontes distintas (critério obrigatório)
    medicoes_dfs = []
    for idx, (fonte_id, fonte_nome) in enumerate(FONTES, 1):
        if fonte_id not in grafo.adj_list:
            print(f"\n[DFS {idx}] Fonte '{fonte_id}' não encontrada — ignorando.")
            continue
        print(f"\n[{idx + len(FONTES)}] DFS (fonte {idx}/3): {fonte_nome}...")
        resultado_dfs, t_dfs_f, t_dfs_min_f, m_dfs_f = _medir(dfs, grafo, fonte_id)
        ordem_dfs, _, _, _, arestas_dfs, tem_ciclo_dfs = resultado_dfs
        tipos_dfs = {}
        for _, _, tipo in arestas_dfs:
            tipos_dfs[tipo] = tipos_dfs.get(tipo, 0) + 1
        print(f"    nós visitados: {len(ordem_dfs)}  |  ciclo: {'SIM' if tem_ciclo_dfs else 'NÃO'}  |  tempo médio: {t_dfs_f} ms")
        medicoes_dfs.append({
            "tarefa": f"DFS fonte {idx} — {fonte_nome}",
            "algoritmo": "DFS recursivo com coloração BRANCO/CINZA/PRETO",
            "origem": fonte_id,
            "musica_origem": fonte_nome,
            "n_runs": N_RUNS,
            "nos_visitados": len(ordem_dfs),
            "ciclo_detectado": tem_ciclo_dfs,
            "classificacao_arestas": tipos_dfs,
            "tempo_medio_ms": t_dfs_f,
            "tempo_min_ms": t_dfs_min_f,
            "memoria_pico_kb": m_dfs_f,
            "complexidade_teorica": "O(V + E)",
            "observacoes": "Percorre todos os vértices do grafo (não apenas um componente).",
        })
    t_dfs     = medicoes_dfs[0]["tempo_medio_ms"] if medicoes_dfs else 0
    t_dfs_min = medicoes_dfs[0]["tempo_min_ms"]   if medicoes_dfs else 0

    print(f"\n[{2 * len(FONTES) + 1}] Dijkstra (fonte única, todos os destinos)...")
    _, t_dij, t_dij_min, m_dij = _medir(dijkstra, grafo, origem)
    print(f"    tempo médio: {t_dij} ms  |  mín: {t_dij_min} ms  |  mem: {m_dij} KB")

    print("\n[4] Bellman-Ford (execução única — O(V*E) é custoso)...")
    _, t_bf, m_bf = _medir_unico(bellman_ford, grafo, origem)
    print(f"    tempo: {t_bf} ms  |  mem: {m_bf} KB")

    print("\n[5] Componentes Conexos (DFS global)...")
    resultado_comp, t_comp, t_comp_min, m_comp = _medir(dfs_componentes_conexos, grafo)
    num_comp = len(resultado_comp)
    print(f"    componentes: {num_comp}  |  tempo médio: {t_comp} ms  |  mem: {m_comp} KB")

    print("\n[6] Bellman-Ford — peso negativo sem ciclo (grafo sintético)...")
    caso_neg = _benchmark_bf_negativo_sem_ciclo()
    print(f"    caminho: {caso_neg['caminho']}  custo: {caso_neg['custo']}  tempo: {caso_neg['tempo_ms']} ms")

    print("\n[7] Bellman-Ford — ciclo negativo detectado (grafo sintético)...")
    caso_ciclo = _benchmark_bf_ciclo_negativo()
    print(f"    ciclo detectado: {caso_ciclo['ciclo_negativo_detectado']}  tempo: {caso_ciclo['tempo_ms']} ms")

    algoritmos = [
        ("BFS",          t_bfs,  t_bfs_min),
        ("DFS",          t_dfs,  t_dfs_min),
        ("Dijkstra",     t_dij,  t_dij_min),
        ("Bellman-Ford", t_bf,   t_bf),
    ]
    mais_rapido = min(algoritmos, key=lambda x: x[1])
    mais_lento  = max(algoritmos, key=lambda x: x[1])

    relatorio = {
        "descricao": (
            "Benchmark dos algoritmos de grafos aplicados ao grafo de "
            "similaridade musical Spotify (Parte 2)."
        ),
        "configuracao": {
            "n_runs": N_RUNS,
            "nota": (
                f"BFS, DFS, Dijkstra e Componentes Conexos executados {N_RUNS}× "
                "para média mais estável. Bellman-Ford executado 1× (O(V*E) é lento)."
            ),
        },
        "grafo": {
            "dataset": "Spotify Tracks — dataset_parte2",
            "vertices": n_v,
            "arestas": n_e,
            "tipo": "não dirigido, ponderado",
            "distribuicao_graus": {
                "minimo": min(len(v) for v in grafo.adj_list.values()),
                "maximo": max(len(v) for v in grafo.adj_list.values()),
                "medio": round(sum(len(v) for v in grafo.adj_list.values()) / n_v, 2),
            },
        },
        "medicoes": [
            {
                "tarefa": "Carregamento do grafo",
                "algoritmo": "leitura de CSV + construção da lista de adjacência",
                "tempo_medio_ms": t_load,
                "tempo_min_ms": t_load_min,
                "memoria_pico_kb": m_load,
                "complexidade_teorica": "O(V + E)",
                "observacoes": "Inclui leitura de arquivo e inserção de todos os nós e arestas.",
            },
            *medicoes_bfs,
            *medicoes_dfs,
            {
                "tarefa": "Dijkstra (caminho mínimo, single-source)",
                "algoritmo": "Dijkstra com heap binário (heapq)",
                "origem": origem,
                "n_runs": N_RUNS,
                "tempo_medio_ms": t_dij,
                "tempo_min_ms": t_dij_min,
                "memoria_pico_kb": m_dij,
                "complexidade_teorica": "O((V + E) log V)",
                "observacoes": (
                    "Calcula distâncias mínimas da origem para todos os demais vértices. "
                    "Pesos = distâncias euclidianas (≥ 0), portanto Dijkstra é adequado."
                ),
            },
            {
                "tarefa": "Bellman-Ford (caminho mínimo, single-source)",
                "algoritmo": "Bellman-Ford iterativo (V-1 relaxamentos)",
                "origem": origem,
                "n_runs": 1,
                "tempo_medio_ms": t_bf,
                "tempo_min_ms": t_bf,
                "memoria_pico_kb": m_bf,
                "complexidade_teorica": "O(V × E)",
                "observacoes": (
                    "Aceita pesos negativos e detecta ciclos negativos. "
                    "Neste dataset os pesos são distâncias euclidianas (≥ 0), "
                    "portanto Dijkstra e Bellman-Ford produzem os mesmos caminhos mínimos."
                ),
            },
            {
                "tarefa": "Componentes Conexos (DFS global)",
                "algoritmo": "DFS iterativo global",
                "n_runs": N_RUNS,
                "tempo_medio_ms": t_comp,
                "tempo_min_ms": t_comp_min,
                "memoria_pico_kb": m_comp,
                "componentes_encontrados": num_comp,
                "complexidade_teorica": "O(V + E)",
                "observacoes": f"Resultado: {num_comp} componente(s) conexo(s).",
            },
        ],
        "casos_especiais_bellman_ford": {
            "descricao": (
                "Grafos direcionados sintéticos para demonstrar as capacidades únicas "
                "do Bellman-Ford: pesos negativos e detecção de ciclos negativos."
            ),
            "peso_negativo_sem_ciclo": caso_neg,
            "ciclo_negativo_detectado": caso_ciclo,
        },
        "resumo_comparativo": {
            "mais_rapido": {"algoritmo": mais_rapido[0], "tempo_medio_ms": mais_rapido[1]},
            "mais_lento":  {"algoritmo": mais_lento[0],  "tempo_medio_ms": mais_lento[1]},
            "razao_bf_vs_dijkstra": round(t_bf / t_dij, 1) if t_dij > 0 else None,
            "razao_bf_vs_bfs":      round(t_bf / t_bfs, 1) if t_bfs > 0 else None,
            "ordem_por_tempo_crescente": sorted(
                [
                    {"algoritmo": "BFS",          "tempo_medio_ms": t_bfs},
                    {"algoritmo": "DFS",          "tempo_medio_ms": t_dfs},
                    {"algoritmo": "Dijkstra",     "tempo_medio_ms": t_dij},
                    {"algoritmo": "Bellman-Ford", "tempo_medio_ms": t_bf},
                ],
                key=lambda x: x["tempo_medio_ms"],
            ),
        },
        "discussao_critica": {
            "BFS": (
                "Ideal para encontrar o caminho com menor número de saltos (grafo não ponderado). "
                "O(V+E), eficiente em memória com fila. Não considera pesos das arestas."
            ),
            "DFS": (
                "Útil para detecção de ciclos, ordenação topológica e componentes fortemente conexos. "
                "O(V+E), mas pode ter pilha de recursão profunda. Não garante caminho mínimo."
            ),
            "Dijkstra": (
                "Algoritmo ótimo para grafos com pesos não negativos. "
                "O((V+E) log V) com heap. Mais rápido que Bellman-Ford na prática. "
                "Falha com pesos negativos."
            ),
            "Bellman-Ford": (
                "Necessário quando há pesos negativos ou para detectar ciclos negativos. "
                "O(V×E) — significativamente mais lento que Dijkstra. "
                "Neste dataset (pesos ≥ 0), Dijkstra é preferível por ser mais eficiente."
            ),
        },
        "metadados": {
            "unidade_tempo": "milissegundos (ms)",
            "unidade_memoria": "kilobytes (KB) — pico alocado durante execução",
            "ferramenta_memoria": "tracemalloc (stdlib Python)",
            "nota": (
                "Tempos medidos com time.perf_counter(). "
                "Variações entre execuções são esperadas por fatores do SO (cache, agendador)."
            ),
        },
    }

    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print("  RESUMO — TEMPO MÉDIO DE EXECUÇÃO")
    print(f"{'='*60}")
    print(f"  {'Algoritmo':<22} {'Médio (ms)':>12}  {'Mín (ms)':>10}  {'Mem (KB)':>10}")
    print(f"  {'-'*22} {'-'*12}  {'-'*10}  {'-'*10}")
    for m in relatorio["medicoes"][1:]:  # índice 0 é o carregamento, não um algoritmo
        print(
            f"  {m['tarefa'][:22]:<22} "
            f"{m['tempo_medio_ms']:>12.4f}  "
            f"{m['tempo_min_ms']:>10.4f}  "
            f"{m['memoria_pico_kb']:>10.2f}"
        )
    print(f"{'='*60}")
    print(f"\n  Mais rápido: {mais_rapido[0]} ({mais_rapido[1]} ms)")
    print(f"  Mais lento : {mais_lento[0]} ({mais_lento[1]} ms)")
    print(f"  BF é {relatorio['resumo_comparativo']['razao_bf_vs_dijkstra']}× mais lento que Dijkstra")
    print(f"\n  Relatório completo: {REPORT_OUT}")


if __name__ == "__main__":
    main()
