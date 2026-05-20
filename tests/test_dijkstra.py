import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graphs.graph import Grafo
from src.graphs.algorithms import dijkstra, dijkstra_caminho

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


def _grafo_com_peso_negativo():

    g = Grafo()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=2.0)
    g.adicionar_aresta("B", "C", peso=-1.0)  
    return g


def _grafo_desconexo():

    g = Grafo()
    for no in ["A", "B", "X", "Y"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B", peso=1.0)
    g.adicionar_aresta("X", "Y", peso=1.0)
    return g

#testes de distâncias
class TestDijkstraDistancias:

    def test_origem_tem_distancia_zero(self):
        
        g = _grafo_simples_ponderado()
        distancias, _ = dijkstra(g, "A")
        assert distancias["A"] == 0.0

    def test_distancias_corretas_grafo_simples(self):

        g = _grafo_simples_ponderado()
        distancias, _ = dijkstra(g, "A")
        assert distancias["A"] == 0.0
        assert distancias["B"] == 1.0
        assert distancias["C"] == 3.0
        assert distancias["D"] == 4.0
        assert distancias["E"] == 4.0   

    def test_distancias_aeroportos_mini(self):

        g = _grafo_aeroportos_mini()
        distancias, _ = dijkstra(g, "REC")
        assert distancias["REC"] == 0.0
        assert distancias["SSA"] == 1.0
        assert distancias["BSB"] == 3.0   
        assert distancias["GIG"] == 4.0   
        assert distancias["GRU"] == 5.0   

    def test_no_inacessivel_tem_distancia_infinita(self):

        g = _grafo_desconexo()
        distancias, _ = dijkstra(g, "A")
        assert distancias["X"] == float("inf")
        assert distancias["Y"] == float("inf")

    def test_peso_zero_aceito(self):

        g = _grafo_peso_zero()
        distancias, _ = dijkstra(g, "A")
        assert distancias["B"] == 0.0
        assert distancias["C"] == 0.0

    def test_simetria_nao_direcionado(self):

        g = _grafo_aeroportos_mini()
        d_ida,  _ = dijkstra(g, "REC")
        d_volta, _ = dijkstra(g, "GRU")
        assert d_ida["GRU"] == d_volta["REC"]

#testes de caminhos
class TestDijkstraCaminhos:

    def test_caminho_correto_a_para_e(self):

        g = _grafo_simples_ponderado()
        custo, caminho = dijkstra_caminho(g, "A", "E")
        assert custo == 4.0
        assert caminho == ["A", "B", "C", "E"]

    def test_caminho_rec_para_gru(self):

        g = _grafo_aeroportos_mini()
        custo, caminho = dijkstra_caminho(g, "REC", "GRU")
        assert custo == 5.0
        assert caminho == ["REC", "SSA", "GIG", "GRU"]

    def test_caminho_para_si_mesmo(self):

        g = _grafo_aeroportos_mini()
        custo, caminho = dijkstra_caminho(g, "REC", "REC")
        assert custo == 0.0
        assert caminho == ["REC"]

    def test_caminho_inacessivel_retorna_none(self):

        g = _grafo_desconexo()
        custo, caminho = dijkstra_caminho(g, "A", "X")
        assert math.isinf(custo)
        assert caminho is None

    def test_caminho_e_consistente_com_distancias(self):
  
        g = _grafo_simples_ponderado()
        distancias, _ = dijkstra(g, "A")
        _, caminho = dijkstra_caminho(g, "A", "E")

        custo_calculado = 0.0
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]

            peso_aresta = next(
                a["peso"] for a in g.adj_list[u] if a["vizinho"] == v
            )
            custo_calculado += peso_aresta

        assert abs(custo_calculado - distancias["E"]) < 1e-9

    def test_caminho_inicia_na_origem_e_termina_no_destino(self):

        g = _grafo_aeroportos_mini()
        _, caminho = dijkstra_caminho(g, "REC", "BSB")
        assert caminho[0] == "REC"
        assert caminho[-1] == "BSB"

    def test_nos_do_caminho_estao_conectados(self):

        g = _grafo_simples_ponderado()
        _, caminho = dijkstra_caminho(g, "A", "E")
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i + 1]
            vizinhos = g.get_vizinhos(u)
            assert v in vizinhos, f"{u} e {v} não são vizinhos no grafo"

#testes de rejeição de pesos negativos
class TestDijkstraPesosNegativos:

    def test_peso_negativo_levanta_value_error(self):

        g = _grafo_com_peso_negativo()
        with pytest.raises(ValueError, match="peso negativo"):
            dijkstra(g, "A")

    def test_dijkstra_caminho_peso_negativo_levanta_erro(self):

        g = _grafo_com_peso_negativo()
        with pytest.raises(ValueError):
            dijkstra_caminho(g, "A", "C")

#testes de robustez
class TestDijkstraRobustez:

    def test_origem_invalida_levanta_erro(self):

        g = _grafo_simples_ponderado()
        with pytest.raises(ValueError):
            dijkstra(g, "Z")

    def test_grafo_um_no(self):

        g = Grafo()
        g.adicionar_no("SOLO")
        distancias, _ = dijkstra(g, "SOLO")
        assert distancias["SOLO"] == 0.0

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
            custo, caminho = dijkstra_caminho(g, origem, destino)
            assert caminho is not None, f"Caminho {origem}→{destino} deveria existir"
            assert custo < float("inf"), f"Custo {origem}→{destino} deveria ser finito"
            assert caminho[0] == origem
            assert caminho[-1] == destino