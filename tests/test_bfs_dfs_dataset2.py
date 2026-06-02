"""
Testes de BFS e DFS aplicados ao 2° dataset (Spotify Tracks — dataset_parte2).

Grafo: similaridade musical KNN (não dirigido, ponderado)
  |V| = 4000   |E| = 19717   componentes conexos = 8

Estrutura do grafo:
  - KNN é calculado DENTRO DO MESMO GÊNERO, portanto o grafo tem
    8 componentes conexos (um por gênero), cada um totalmente conexo.
  - ORIGEM e DESTINO pertencem ao componente 'brazil' (513 vértices).
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graphs.io import ler_musicas, ler_adjacencias_musicas
from src.graphs.algorithms import (
    bfs,
    bfs_caminho,
    bfs_por_niveis,
    dfs,
    dfs_detectar_ciclo,
    dfs_componentes_conexos,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
NOS_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "musicas_nos.csv")
ADJ_CSV  = os.path.join(BASE_DIR, "data", "dataset_parte2", "adjacencias_musicas.csv")

# nós do componente 'brazil' (maior componente, 513 vértices)
ORIGEM  = "3pyQ7RB5P8iwZMkPAeZ3ym"
DESTINO = "4cpdzzOLPuoRLnaJBcQFYp"

NUM_VERTICES    = 513   # tamanho do componente ao qual ORIGEM pertence
NUM_COMPONENTES = 8     # um por gênero (brazil, pop, funk, hip-hop, rock, electronic, country, latin)


@pytest.fixture(scope="module")
def grafo_spotify():
    g = ler_musicas(NOS_CSV)
    ler_adjacencias_musicas(g, ADJ_CSV)
    return g


class TestBFSDataset2:

    def test_bfs_visita_todos_nos_do_componente(self, grafo_spotify):
        """BFS deve visitar todos os vértices do componente ao qual ORIGEM pertence."""
        ordem, _, _, _ = bfs(grafo_spotify, ORIGEM)
        assert len(ordem) == NUM_VERTICES

    def test_bfs_nivel_origem_e_zero(self, grafo_spotify):
        """O nível da origem deve ser 0."""
        _, niveis, _, _ = bfs(grafo_spotify, ORIGEM)
        assert niveis[ORIGEM] == 0

    def test_bfs_vizinhos_diretos_no_nivel_1(self, grafo_spotify):
        """Todos os vizinhos diretos da origem devem estar no nível 1."""
        _, niveis, _, _ = bfs(grafo_spotify, ORIGEM)
        for v in grafo_spotify.get_vizinhos(ORIGEM):
            assert niveis[v] == 1, (
                f"Vizinho direto {v} está no nível {niveis[v]}, esperado 1"
            )

    def test_bfs_niveis_consistentes_com_predecessores(self, grafo_spotify):
        """Para todo nó v com predecessor p: nivel[v] == nivel[p] + 1."""
        _, niveis, predecessores, _ = bfs(grafo_spotify, ORIGEM)
        for no, pred in predecessores.items():
            if pred is not None:
                assert niveis[no] == niveis[pred] + 1, (
                    f"Inconsistência: nivel[{no}]={niveis[no]}, nivel[{pred}]={niveis[pred]}"
                )

    def test_bfs_arestas_arvore_formam_arvore_geradora(self, grafo_spotify):
        """Em grafo conexo, o número de arestas de árvore BFS deve ser |V| - 1."""
        _, _, _, arestas_tipo = bfs(grafo_spotify, ORIGEM)
        arvore = [(u, v) for u, v, t in arestas_tipo if t == "arvore"]
        assert len(arvore) == NUM_VERTICES - 1

    def test_bfs_todos_nos_tem_nivel(self, grafo_spotify):
        """Todo vértice visitado deve ter um nível atribuído."""
        ordem, niveis, _, _ = bfs(grafo_spotify, ORIGEM)
        for no in ordem:
            assert no in niveis

    def test_bfs_predecessor_da_origem_e_none(self, grafo_spotify):
        """A origem não tem predecessor."""
        _, _, predecessores, _ = bfs(grafo_spotify, ORIGEM)
        assert predecessores[ORIGEM] is None

    def test_bfs_predecessores_sao_nos_validos(self, grafo_spotify):
        """Todo predecessor deve ser um nó existente no grafo."""
        todos_nos = set(grafo_spotify.get_nos())
        _, _, predecessores, _ = bfs(grafo_spotify, ORIGEM)
        for no, pred in predecessores.items():
            if pred is not None:
                assert pred in todos_nos

    def test_bfs_caminho_entre_duas_musicas(self, grafo_spotify):
        """BFS deve encontrar caminho entre dois nós do mesmo componente."""
        caminho = bfs_caminho(grafo_spotify, ORIGEM, DESTINO)
        assert caminho is not None
        assert caminho[0] == ORIGEM
        assert caminho[-1] == DESTINO

    def test_bfs_caminho_comprimento_minimo(self, grafo_spotify):
        """O caminho BFS deve ter 5 nós (4 saltos) entre ORIGEM e DESTINO."""
        caminho = bfs_caminho(grafo_spotify, ORIGEM, DESTINO)
        assert len(caminho) == 5

    def test_bfs_caminho_usa_apenas_arestas_validas(self, grafo_spotify):
        """Cada par consecutivo do caminho BFS deve ser vizinhos no grafo."""
        caminho = bfs_caminho(grafo_spotify, ORIGEM, DESTINO)
        for i in range(len(caminho) - 1):
            vizinhos = grafo_spotify.get_vizinhos(caminho[i])
            assert caminho[i + 1] in vizinhos, (
                f"Aresta inválida no caminho: {caminho[i]} → {caminho[i+1]}"
            )

    def test_bfs_caminho_para_si_mesmo(self, grafo_spotify):
        """Caminho de um nó para ele mesmo é uma lista com apenas o próprio nó."""
        caminho = bfs_caminho(grafo_spotify, ORIGEM, ORIGEM)
        assert caminho == [ORIGEM]

    def test_bfs_por_niveis_camada_zero_tem_so_origem(self, grafo_spotify):
        """A camada 0 do BFS por níveis deve conter apenas a origem."""
        camadas = bfs_por_niveis(grafo_spotify, ORIGEM)
        assert camadas[0] == [ORIGEM]

    def test_bfs_por_niveis_soma_total_igual_componente(self, grafo_spotify):
        """A soma dos nós em todas as camadas deve ser igual ao tamanho do componente."""
        camadas = bfs_por_niveis(grafo_spotify, ORIGEM)
        assert sum(len(c) for c in camadas) == NUM_VERTICES

    def test_bfs_nivel_maximo(self, grafo_spotify):
        """O nível máximo atingido pelo BFS neste componente deve ser 7."""
        _, niveis, _, _ = bfs(grafo_spotify, ORIGEM)
        assert max(niveis.values()) == 7


class TestDFSDataset2:

    def test_dfs_visita_todos_nos(self, grafo_spotify):
        """DFS global visita todos os 4000 vértices do grafo (todos os componentes)."""
        ordem, _, _, _, _, _ = dfs(grafo_spotify, ORIGEM)
        assert len(ordem) == 4000

    def test_dfs_origem_esta_na_ordem_de_visita(self, grafo_spotify):
        """A origem deve aparecer na ordem de visita (DFS global, não necessariamente primeiro)."""
        ordem, _, _, _, _, _ = dfs(grafo_spotify, ORIGEM)
        assert ORIGEM in ordem

    def test_dfs_detecta_ciclo_real(self, grafo_spotify):
        """Grafo KNN com 4000 vértices e 19717 arestas possui ciclos reais."""
        _, _, _, _, _, tem_ciclo = dfs(grafo_spotify, ORIGEM)
        assert tem_ciclo is True

    def test_dfs_helper_detectar_ciclo(self, grafo_spotify):
        """dfs_detectar_ciclo() deve confirmar a presença de ciclos."""
        assert dfs_detectar_ciclo(grafo_spotify) is True

    def test_dfs_todos_nos_tem_tempo_entrada(self, grafo_spotify):
        """Todo vértice visitado deve ter tempo de entrada registrado."""
        ordem, _, t_entrada, _, _, _ = dfs(grafo_spotify, ORIGEM)
        for no in ordem:
            assert no in t_entrada

    def test_dfs_todos_nos_tem_tempo_saida(self, grafo_spotify):
        """Todo vértice visitado deve ter tempo de saída registrado."""
        ordem, _, _, t_saida, _, _ = dfs(grafo_spotify, ORIGEM)
        for no in ordem:
            assert no in t_saida

    def test_dfs_tempo_entrada_menor_que_saida(self, grafo_spotify):
        """Invariante do DFS: tempo_entrada[u] < tempo_saida[u] para todo u."""
        ordem, _, t_entrada, t_saida, _, _ = dfs(grafo_spotify, ORIGEM)
        for no in ordem:
            assert t_entrada[no] < t_saida[no], (
                f"Nó {no}: entrada={t_entrada[no]} >= saída={t_saida[no]}"
            )

    def test_dfs_tempos_sao_unicos(self, grafo_spotify):
        """Todos os timestamps de entrada e saída devem ser distintos."""
        ordem, _, t_entrada, t_saida, _, _ = dfs(grafo_spotify, ORIGEM)
        todos = list(t_entrada.values()) + list(t_saida.values())
        assert len(todos) == len(set(todos)), "Timestamps duplicados encontrados"

    def test_dfs_ancestral_tem_entrada_menor(self, grafo_spotify):
        """O predecessor de cada nó deve ter tempo de entrada estritamente menor."""
        _, predecessores, t_entrada, _, _, _ = dfs(grafo_spotify, ORIGEM)
        for no, pred in predecessores.items():
            if pred is not None and no in t_entrada and pred in t_entrada:
                assert t_entrada[pred] < t_entrada[no], (
                    f"Predecessor {pred} (entrada={t_entrada[pred]}) "
                    f"deveria entrar antes de {no} (entrada={t_entrada[no]})"
                )

    def test_dfs_arestas_arvore_cobrem_todos_nos(self, grafo_spotify):
        """Arestas de árvore DFS global = |V| - |componentes| = 4000 - 8 = 3992."""
        _, _, _, _, arestas_tipo, _ = dfs(grafo_spotify, ORIGEM)
        vistas = set()
        arvore = []
        for u, v, t in arestas_tipo:
            chave = (min(u, v), max(u, v))
            if chave not in vistas and t == "arvore":
                vistas.add(chave)
                arvore.append((u, v))
        assert len(arvore) == 4000 - NUM_COMPONENTES

    def test_dfs_componentes_conexos_retorna_oito(self, grafo_spotify):
        """O grafo tem 8 componentes conexos (um por gênero, pois KNN é intra-gênero)."""
        componentes = dfs_componentes_conexos(grafo_spotify)
        assert len(componentes) == NUM_COMPONENTES

    def test_dfs_componentes_somam_todos_nos(self, grafo_spotify):
        """A soma dos vértices em todos os componentes deve ser |V| = 4000."""
        componentes = dfs_componentes_conexos(grafo_spotify)
        assert sum(len(c) for c in componentes) == 4000

    def test_dfs_maior_componente_contem_origem(self, grafo_spotify):
        """O maior componente deve conter a ORIGEM (gênero brazil, 513 vértices)."""
        componentes = dfs_componentes_conexos(grafo_spotify)
        maior = max(componentes, key=len)
        assert ORIGEM in maior
        assert len(maior) == NUM_VERTICES

    def test_dfs_sem_falso_ciclo_em_grafo_linear(self):
        """Regressão: grafo linear não-dirigido NÃO deve ser detectado como cíclico."""
        from src.graphs.graph import Grafo
        g = Grafo()
        for no in ["A", "B", "C", "D", "E"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B")
        g.adicionar_aresta("B", "C")
        g.adicionar_aresta("C", "D")
        g.adicionar_aresta("D", "E")
        _, _, _, _, _, tem_ciclo = dfs(g, "A")
        assert tem_ciclo is False, (
            "Grafo linear foi detectado como cíclico (falso positivo no DFS)"
        )

    def test_dfs_sem_falso_ciclo_em_arvore(self):
        """Regressão: árvore não-dirigida NÃO deve ser detectada como cíclica."""
        from src.graphs.graph import Grafo
        g = Grafo()
        for no in ["R", "A", "B", "C", "D", "E"]:
            g.adicionar_no(no)
        g.adicionar_aresta("R", "A")
        g.adicionar_aresta("R", "B")
        g.adicionar_aresta("A", "C")
        g.adicionar_aresta("A", "D")
        g.adicionar_aresta("B", "E")
        _, _, _, _, _, tem_ciclo = dfs(g, "R")
        assert tem_ciclo is False, (
            "Árvore não-dirigida foi detectada como cíclica (falso positivo no DFS)"
        )
