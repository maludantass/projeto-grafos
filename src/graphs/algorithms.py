#BFS, DFS e Dijikstra implementados (parte 1)

import heapq
from collections import deque

# BFS
def bfs(grafo, origem):
    
    if origem not in grafo.adj_list:
        raise ValueError(f"Nó de origem '{origem}' não foi encontrado no grafo.")

    visitados     = {origem}
    niveis        = {origem: 0}
    predecessores = {origem: None}
    ordem_visita  = []
    arestas_tipo  = []

    fila = deque([origem])

    while fila:
        atual = fila.popleft()
        ordem_visita.append(atual)

        for aresta in grafo.adj_list.get(atual, []):
            vizinho = aresta["vizinho"]
            if vizinho not in visitados:
                visitados.add(vizinho)
                niveis[vizinho]        = niveis[atual] + 1
                predecessores[vizinho] = atual
                arestas_tipo.append((atual, vizinho, "arvore"))
                fila.append(vizinho)
            else:
                arestas_tipo.append((atual, vizinho, "cruzada"))

    return ordem_visita, niveis, predecessores, arestas_tipo


def bfs_caminho(grafo, origem, destino):

    _, _, predecessores, _ = bfs(grafo, origem) #para ignorar valores
    return _reconstruir_caminho(predecessores, origem, destino)

def bfs_por_niveis(grafo, origem):
 
    _, niveis, _, _ = bfs(grafo, origem)
    if not niveis:
        return []
    max_nivel = max(niveis.values())
    camadas = [[] for _ in range(max_nivel + 1)]
    for no, nivel in niveis.items():
        camadas[nivel].append(no)
    return camadas

# DFS
def dfs(grafo, origem):
   
    if origem not in grafo.adj_list:
        raise ValueError(f"Nó de origem '{origem}' não foi encontrado no grafo.")

    BRANCO = 0  #não foi visitado
    CINZA  = 1  #ta na pilha
    PRETO  = 2  #finalizado

    cor           = {no: BRANCO for no in grafo.get_nos()}
    predecessores = {no: None   for no in grafo.get_nos()}
    tempo_entrada = {}
    tempo_saida   = {}
    ordem_visita  = []
    arestas_tipo  = []
    tem_ciclo     = False
    tempo         = [0] 

    def _visitar(u):
        nonlocal tem_ciclo
        cor[u]           = CINZA
        tempo[0]        += 1
        tempo_entrada[u] = tempo[0]
        ordem_visita.append(u)

        for aresta in grafo.adj_list.get(u, []):
            v = aresta["vizinho"]
            if cor[v] == BRANCO:
                predecessores[v] = u
                arestas_tipo.append((u, v, "arvore"))
                _visitar(v)
            elif cor[v] == CINZA:
                arestas_tipo.append((u, v, "retorno"))
                tem_ciclo = True
            elif cor[v] == PRETO:
                if tempo_entrada.get(u, 0) < tempo_entrada.get(v, 0):
                    arestas_tipo.append((u, v, "avanco"))
                else:
                    arestas_tipo.append((u, v, "cruzada"))

        cor[u]          = PRETO
        tempo[0]       += 1
        tempo_saida[u]  = tempo[0]

    for no in grafo.get_nos():
        if cor[no] == BRANCO:
            _visitar(no)

    return ordem_visita, predecessores, tempo_entrada, tempo_saida, arestas_tipo, tem_ciclo


def dfs_detectar_ciclo(grafo):

    _, _, _, _, _, tem_ciclo = dfs(grafo, grafo.get_nos()[0])
    return tem_ciclo


def dfs_componentes_conexos(grafo):

    visitados  = set()
    componentes = []

    def _explorar(origem):
        pilha     = [origem]
        componente = []
        while pilha:
            atual = pilha.pop()
            if atual in visitados:
                continue
            visitados.add(atual)
            componente.append(atual)
            for aresta in grafo.adj_list.get(atual, []):
                if aresta["vizinho"] not in visitados:
                    pilha.append(aresta["vizinho"])
        return componente

    for no in grafo.get_nos():
        if no not in visitados:
            componentes.append(_explorar(no))

    return componentes


# Dijkstra 
def dijkstra(grafo, origem):
    
    if origem not in grafo.adj_list:
        raise ValueError(f"Nó de origem '{origem}' não foi encontrado no grafo.")

    for no in grafo.get_nos(): #pra ver se tem negativo, já q dijisktra n aceita
        for aresta in grafo.adj_list.get(no, []):
            if aresta["peso"] < 0:
                raise ValueError(
                    f"Dijkstra não aceita pesos negativos. "
                    f"Aresta {no}→{aresta['vizinho']} tem peso {aresta['peso']}."
                )

    distancias    = {no: float("inf") for no in grafo.get_nos()}
    predecessores = {no: None         for no in grafo.get_nos()}
    distancias[origem] = 0.0

    heap     = [(0.0, origem)]
    visitados = set()

    while heap:
        custo_atual, no_atual = heapq.heappop(heap)

        if no_atual in visitados:
            continue
        visitados.add(no_atual)

        for aresta in grafo.adj_list.get(no_atual, []):
            vizinho   = aresta["vizinho"]
            novo_custo = custo_atual + aresta["peso"]

            if novo_custo < distancias[vizinho]:
                distancias[vizinho]    = novo_custo
                predecessores[vizinho] = no_atual
                heapq.heappush(heap, (novo_custo, vizinho))

    return distancias, predecessores


def dijkstra_caminho(grafo, origem, destino):
 
    distancias, predecessores = dijkstra(grafo, origem)
    custo   = distancias.get(destino, float("inf"))
    caminho = _reconstruir_caminho(predecessores, origem, destino)
    return custo, caminho


def _reconstruir_caminho(predecessores, origem, destino):
    caminho = []
    atual   = destino
    while atual is not None:
        caminho.append(atual)
        atual = predecessores.get(atual)
    caminho.reverse()
    if not caminho or caminho[0] != origem:
        return None
    return caminho