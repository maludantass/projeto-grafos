#PARTE 6 - DISTANCIA USANDO DIJKSTRA
import os
import sys
import csv
import heapq

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias
from pathlib import Path


def dijkstra(grafo, origem):
    # Implementação do algoritmo de Dijkstra para grafos ponderados.
    #Retorna dicionários de distâncias mínimas e predecessores a partir da origem.

    distancias = {no: float('inf') for no in grafo.get_nos()}
    predecessores = {no: None for no in grafo.get_nos()}
    distancias[origem] = 0.0

    # Heap: (custo_acumulado, nó)
    heap = [(0.0, origem)]

    visitados = set()

    while heap:
        custo_atual, no_atual = heapq.heappop(heap)

        if no_atual in visitados:
            continue
        visitados.add(no_atual)

        for aresta in grafo.adj_list.get(no_atual, []):
            vizinho = aresta['vizinho']
            peso = aresta['peso']
            novo_custo = custo_atual + peso

            if novo_custo < distancias[vizinho]:
                distancias[vizinho] = novo_custo
                predecessores[vizinho] = no_atual
                heapq.heappush(heap, (novo_custo, vizinho))

    return distancias, predecessores


def reconstruir_caminho(predecessores, origem, destino):
    #Reconstrói o caminho mínimo do destino até a origem via predecessores.
    caminho = []
    atual = destino

    while atual is not None:
        caminho.append(atual)
        atual = predecessores[atual]

    caminho.reverse()

    if not caminho or caminho[0] != origem:
        return None  # Destino inacessível

    return caminho


def calcular_rotas(grafo, pares):
    #Calcula a rota de menor custo para cada par.
    #Retorna lista de dicts com: origem, destino, custo, caminho.

    resultados = []

    for origem, destino in pares:
        if origem not in grafo.get_nos():
            print(f" AVISO: Aeroporto '{origem}' não encontrado no grafo.")
            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": None,
                "caminho": "AEROPORTO_INVALIDO"
            })
            continue

        if destino not in grafo.get_nos():
            print(f" AVISO: Aeroporto '{destino}' não encontrado no grafo.")
            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": None,
                "caminho": "AEROPORTO_INVALIDO"
            })
            continue

        distancias, predecessores = dijkstra(grafo, origem)

        custo = distancias[destino]
        caminho = reconstruir_caminho(predecessores, origem, destino)

        if caminho is None or custo == float('inf'):
            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": None,
                "caminho": "INACESSIVEL"
            })
        else:
            resultados.append({
                "origem": origem,
                "destino": destino,
                "custo": round(custo, 2),
                "caminho": " -> ".join(caminho)
            })

    return resultados


def ler_rotas_csv(caminho):
    #Leitura de  pares de origem e destino do arquivo data/rotas.csv.
    pares = []
    with open(caminho, mode='r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            origem = linha.get('origem', '').strip().upper()
            destino = linha.get('destino', '').strip().upper()
            if origem and destino:
                pares.append((origem, destino))
    return pares


def salvar_distancias_csv(resultados, caminho_saida):
    #Salva os resultados em out/distancias_rotas.csv.
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_saida, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origem', 'destino', 'custo', 'caminho'])
        writer.writeheader()
        writer.writerows(resultados)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_nos = os.path.join(base_dir, "data", "aeroportos_data.csv")
    arquivo_arestas = os.path.join(base_dir, "data", "adjacencias_aeroportos.csv")
    arquivo_rotas = os.path.join(base_dir, "data", "rotas.csv")
    out_dir = os.path.join(base_dir, "out")

    print("Carregando grafo...")
    grafo = ler_aeroportos(arquivo_nos)
    ler_adjacencias(grafo, arquivo_arestas)
    print(grafo)

    print("\nLendo pares de rotas...")
    pares = ler_rotas_csv(arquivo_rotas)
    print(f"  {len(pares)} pares encontrados.")

    print("\n")
    print("DISTÂNCIAS COM DIJKSTRA")

    resultados = calcular_rotas(grafo, pares)

    print(f"\n{'Origem':<6} {'Destino':<8} {'Custo':>6}  Caminho")
    print(f"{'-'*6} {'-'*8} {'-'*6}  {'-'*40}")
    for r in resultados:
        custo_str = str(r['custo']) if r['custo'] is not None else "N/A"
        print(f"{r['origem']:<6} {r['destino']:<8} {custo_str:>6}  {r['caminho']}")

    caminho_saida = os.path.join(out_dir, "distancias_rotas.csv")
    salvar_distancias_csv(resultados, caminho_saida)
    print(f"\nArquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    main()