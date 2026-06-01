import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graphs.graph import Grafo
from src.graphs.algorithms import bellman_ford, bellman_ford_caminho


def _grafo_simples_ponderado():
    g = Grafo()
    for no in ["A", "B", "C", "D", "E"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=1.0)
    g.adicionar_aresta("B", "C", peso=2.0)
    g.adicionar_aresta("C", "E", peso=1.0)
    g.adicionar_aresta("A", "D", peso=4.0)
    g.adicionar_aresta("D", "E", peso=1.0)
    return g


def _grafo_aeroportos_mini():
    g = Grafo()
    for no in ["REC", "SSA", "GIG", "GRU", "BSB"]:
        g.adicionar_no(no)
    g.adicionar_aresta("REC", "SSA", peso=1.0)
    g.adicionar_aresta("SSA", "GIG", peso=3.0)
    g.adicionar_aresta("GIG", "GRU", peso=1.0)
    g.adicionar_aresta("SSA", "BSB", peso=2.0)
    return g


def _grafo_peso_zero():
    g = Grafo()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=0.0)
    g.adicionar_aresta("B", "C", peso=0.0)
    return g


def _grafo_desconexo():
    g = Grafo()
    for no in ["A", "B", "X", "Y"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=1.0)
    g.adicionar_aresta("X", "Y", peso=1.0)
    return g


def _grafo_spotify_mini():
    g = Grafo()
    musicas = ["ska_01", "ska_02", "pop_01", "jazz_01", "jazz_02"]
    for m in musicas:
        g.adicionar_no(m)
    g.adicionar_aresta("ska_01", "ska_02",  peso=0.12)
    g.adicionar_aresta("ska_02", "pop_01",  peso=0.45)
    g.adicionar_aresta("pop_01", "jazz_01", peso=0.31)
    g.adicionar_aresta("jazz_01","jazz_02", peso=0.08)
    g.adicionar_aresta("ska_01", "jazz_02", peso=0.95)
    return g


class TestBellmanFordDistancias:

    def test_origem_tem_distancia_zero(self):
        g = _grafo_simples_ponderado()
        distancias, _ = bellman_ford(g, "A")
        assert distancias["A"] == 0.0

    def test_distancias_corretas_grafo_simples(self):
        g = _grafo_simples_ponderado()
        distancias, _ = bellman_ford(g, "A")
        assert distancias["A"] == 0.0
        assert distancias["B"] == 1.0
        assert distancias["C"] == 3.0
        assert distancias["D"] == 4.0
        assert distancias["E"] == 4.0   

    def test_distancias_aeroportos_mini(self):
        g = _grafo_aeroportos_mini()
        distancias, _ = bellman_ford(g, "REC")
        assert distancias["REC"] == 0.0
        assert distancias["SSA"] == 1.0
        assert distancias["BSB"] == 3.0
        assert distancias["GIG"] == 4.0
        assert distancias["GRU"] == 5.0

    def test_no_inacessivel_tem_distancia_infinita(self):
        g = _grafo_desconexo()
        distancias, _ = bellman_ford(g, "A")
        assert distancias["X"] == float("inf")
        assert distancias["Y"] == float("inf")

    def test_peso_zero_aceito(self):
        g = _grafo_peso_zero()
        distancias, _ = bellman_ford(g, "A")
        assert distancias["B"] == 0.0
        assert distancias["C"] == 0.0

    def test_simetria_nao_direcionado(self):
        g = _grafo_aeroportos_mini()
        d_ida,   _ = bellman_ford(g, "REC")
        d_volta, _ = bellman_ford(g, "GRU")
        assert d_ida["GRU"] == d_volta["REC"]

    def test_grafo_spotify_mini_distancias(self):
        g = _grafo_spotify_mini()
        distancias, _ = bellman_ford(g, "ska_01")
        assert distancias["ska_01"]  == 0.0
        assert distancias["ska_02"]  == pytest.approx(0.12, abs=1e-9)
        assert distancias["pop_01"]  == pytest.approx(0.57, abs=1e-9)
        assert distancias["jazz_02"] == pytest.approx(0.95, abs=1e-9)


class TestBellmanFordCaminhos:

    def test_caminho_correto_a_para_e(self):
        g = _grafo_simples_ponderado()
        custo, caminho = bellman_ford_caminho(g, "A", "E")
        assert custo == 4.0
        assert caminho == ["A", "B", "C", "E"]

    def test_caminho_rec_para_gru(self):
        g = _grafo_aeroportos_mini()
        custo, caminho = bellman_ford_caminho(g, "REC", "GRU")
        assert custo == 5.0
        assert caminho == ["REC", "SSA", "GIG", "GRU"]

    def test_caminho_para_si_mesmo(self):
        g = _grafo_aeroportos_mini()
        custo, caminho = bellman_ford_caminho(g, "REC", "REC")
        assert custo == 0.0
        assert caminho == ["REC"]

    def test_caminho_inacessivel_retorna_none(self):
        g = _grafo_desconexo()
        custo, caminho = bellman_ford_caminho(g, "A", "X")
        assert math.isinf(custo)
        assert caminho is None

    def test_caminho_inicia_na_origem_e_termina_no_destino(self):
        g = _grafo_aeroportos_mini()
        _, caminho = bellman_ford_caminho(g, "REC", "BSB")
        assert caminho[0] == "REC"
        assert caminho[-1] == "BSB"

    def test_nos_do_caminho_estao_conectados(self):
        g = _grafo_simples_ponderado()
        _, caminho = bellman_ford_caminho(g, "A", "E")
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            vizinhos = g.get_vizinhos(u)
            assert v in vizinhos, f"{u} e {v} não são vizinhos no grafo"

    def test_caminho_e_consistente_com_distancias(self):
        g = _grafo_simples_ponderado()
        distancias, _ = bellman_ford(g, "A")
        _, caminho = bellman_ford_caminho(g, "A", "E")

        custo_calculado = 0.0
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            peso_aresta = next(
                a["peso"] for a in g.adj_list[u] if a["vizinho"] == v
            )
            custo_calculado += peso_aresta

        assert abs(custo_calculado - distancias["E"]) < 1e-9

    def test_cinco_pares_obrigatorios_aeroportos(self):
        g = _grafo_aeroportos_mini()
        pares = [
            ("REC", "GRU"),
            ("REC", "BSB"),
            ("SSA", "GRU"),
            ("BSB", "GIG"),
            ("GIG", "REC"),
        ]
        for origem, destino in pares:
            custo, caminho = bellman_ford_caminho(g, origem, destino)
            assert caminho is not None, f"Caminho {origem}→{destino} deveria existir"
            assert custo < float("inf"), f"Custo {origem}→{destino} deveria ser finito"
            assert caminho[0] == origem
            assert caminho[-1] == destino

    def test_caminho_spotify_mini(self):
        g = _grafo_spotify_mini()
        custo, caminho = bellman_ford_caminho(g, "ska_01", "jazz_01")
        assert caminho is not None
        assert caminho[0] == "ska_01"
        assert caminho[-1] == "jazz_01"
        custo_real = sum(
            next(a["peso"] for a in g.adj_list[caminho[i]] if a["vizinho"] == caminho[i + 1])
            for i in range(len(caminho) - 1)
        )
        assert abs(custo - custo_real) < 1e-9


class TestBellmanFordPesosNegativos:

    def test_aresta_negativa_em_grafo_nao_direcionado_e_ciclo_negativo(self):
        g = Grafo()
        for no in ["A", "B", "C"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=3.0)
        g.adicionar_aresta("B", "C", peso=-1.0)

        with pytest.raises(ValueError, match="negativo"):
            bellman_ford(g, "A")

    def test_bellman_ford_caminho_com_ciclo_negativo_lanca_erro(self):
        g = Grafo()
        for no in ["A", "B", "C"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=3.0)
        g.adicionar_aresta("B", "C", peso=-1.0)

        with pytest.raises(ValueError, match="negativo"):
            bellman_ford_caminho(g, "A", "C")

    def test_ambos_algoritmos_rejeitam_peso_negativo_em_nao_direcionado(self):
        from src.graphs.algorithms import dijkstra
        g = Grafo()
        for no in ["X", "Y", "Z"]:
            g.adicionar_no(no)
        g.adicionar_aresta("X", "Y", peso=5.0)
        g.adicionar_aresta("Y", "Z", peso=-2.0)

        with pytest.raises(ValueError):
            dijkstra(g, "X")

        with pytest.raises(ValueError):
            bellman_ford(g, "X")

    def test_grafo_direcionado_aceita_peso_negativo_sem_ciclo(self):
        from src.graphs.graph import GrafoDirecionado
        g = GrafoDirecionado()
        for no in ["A", "B", "C", "D"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=5.0)
        g.adicionar_aresta("B", "C", peso=-2.0)
        g.adicionar_aresta("C", "D", peso=1.0)
        g.adicionar_aresta("B", "D", peso=4.0)

        distancias, _ = bellman_ford(g, "A")
        assert distancias["A"] == 0.0
        assert distancias["B"] == pytest.approx(5.0,  abs=1e-9)
        assert distancias["C"] == pytest.approx(3.0,  abs=1e-9) 
        assert distancias["D"] == pytest.approx(4.0,  abs=1e-9)  

    def test_grafo_direcionado_caminho_com_peso_negativo(self):
        from src.graphs.graph import GrafoDirecionado
        g = GrafoDirecionado()
        for no in ["A", "B", "C", "D"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=5.0)
        g.adicionar_aresta("B", "C", peso=-2.0)
        g.adicionar_aresta("C", "D", peso=1.0)
        g.adicionar_aresta("B", "D", peso=4.0)

        custo, caminho = bellman_ford_caminho(g, "A", "D")
        assert caminho == ["A", "B", "C", "D"]
        assert custo == pytest.approx(4.0, abs=1e-9)

    def test_grafo_direcionado_dijkstra_rejeita_peso_negativo(self):
        from src.graphs.graph import GrafoDirecionado
        from src.graphs.algorithms import dijkstra
        g = GrafoDirecionado()
        for no in ["A", "B", "C", "D"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=5.0)
        g.adicionar_aresta("B", "C", peso=-2.0)
        g.adicionar_aresta("C", "D", peso=1.0)
        g.adicionar_aresta("B", "D", peso=4.0)

        with pytest.raises(ValueError):
            dijkstra(g, "A")

    def test_grafo_direcionado_ciclo_negativo_detectado(self):
        from src.graphs.graph import GrafoDirecionado
        g = GrafoDirecionado()
        for no in ["A", "B", "C"]:
            g.adicionar_no(no)
        g.adicionar_aresta("A", "B", peso=1.0)
        g.adicionar_aresta("B", "C", peso=-3.0)
        g.adicionar_aresta("C", "A", peso=1.0)

        with pytest.raises(ValueError, match="negativo"):
            bellman_ford(g, "A")


class TestBellmanFordConsistenciaDijkstra:

    def test_mesmas_distancias_grafo_simples(self):
        from src.graphs.algorithms import dijkstra
        g = _grafo_simples_ponderado()
        dist_dij, _ = dijkstra(g, "A")
        dist_bf,  _ = bellman_ford(g, "A")
        for no in g.get_nos():
            assert abs(dist_dij[no] - dist_bf[no]) < 1e-9, \
                f"Divergência no nó {no}: Dijkstra={dist_dij[no]}, BF={dist_bf[no]}"

    def test_mesmas_distancias_aeroportos(self):
        from src.graphs.algorithms import dijkstra
        g = _grafo_aeroportos_mini()
        dist_dij, _ = dijkstra(g, "REC")
        dist_bf,  _ = bellman_ford(g, "REC")
        for no in g.get_nos():
            assert abs(dist_dij[no] - dist_bf[no]) < 1e-9, \
                f"Divergência no nó {no}: Dijkstra={dist_dij[no]}, BF={dist_bf[no]}"

    def test_mesmas_distancias_spotify_mini(self):
        from src.graphs.algorithms import dijkstra
        g = _grafo_spotify_mini()
        dist_dij, _ = dijkstra(g, "ska_01")
        dist_bf,  _ = bellman_ford(g, "ska_01")
        for no in g.get_nos():
            assert abs(dist_dij[no] - dist_bf[no]) < 1e-9, \
                f"Divergência no nó {no}: Dijkstra={dist_dij[no]}, BF={dist_bf[no]}"


class TestBellmanFordRobustez:

    def test_origem_invalida_levanta_erro(self):
        g = _grafo_simples_ponderado()
        with pytest.raises(ValueError, match="não foi encontrado"):
            bellman_ford(g, "Z")

    def test_grafo_um_no(self):
        g = Grafo()
        g.adicionar_no("SOLO")
        distancias, _ = bellman_ford(g, "SOLO")
        assert distancias["SOLO"] == 0.0

    def test_grafo_linear_longo(self):
        """Garante convergência correta em cadeia A→B→C→D→E→F→G."""
        g = Grafo()
        nos = list("ABCDEFG")
        for no in nos:
            g.adicionar_no(no)
        for i in range(len(nos) - 1):
            g.adicionar_aresta(nos[i], nos[i + 1], peso=1.0)
        distancias, _ = bellman_ford(g, "A")
        for i, no in enumerate(nos):
            assert distancias[no] == float(i), f"Distância de A a {no} deveria ser {i}"