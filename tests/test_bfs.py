import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graphs.graph import Grafo #importando das pastas
from src.graphs.algorithms import bfs, bfs_caminho, bfs_por_niveis

def _grafo_linear():
    
    g = Grafo()
    for no in ["A", "B", "C", "D"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("C", "D")
    return g

def _grafo_estrela():
    
    g = Grafo()
    for no in ["C", "F1", "F2", "F3", "F4"]:
        g.adicionar_no(no)
    for f in ["F1", "F2", "F3", "F4"]:
        g.adicionar_aresta("C", f)
    return g


def _grafo_ciclo():

    g = Grafo()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("C", "A")
    return g


def _grafo_desconexo():

    g = Grafo()
    for no in ["A", "B", "C", "X", "Y"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("X", "Y")
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

#testes de níveis/camadas
class TestBFSNiveis:

    def test_niveis_grafo_linear(self):

        g = _grafo_linear()
        _, niveis, _, _ = bfs(g, "A")
        assert niveis["A"] == 0
        assert niveis["B"] == 1
        assert niveis["C"] == 2
        assert niveis["D"] == 3

    def test_niveis_grafo_estrela(self):

        g = _grafo_estrela()
        _, niveis, _, _ = bfs(g, "C")
        assert niveis["C"] == 0
        for f in ["F1", "F2", "F3", "F4"]:
            assert niveis[f] == 1

    def test_nivel_origem_sempre_zero(self):

        for fonte in ["A", "B", "C", "D"]:
            g = _grafo_linear()
            _, niveis, _, _ = bfs(g, fonte)
            assert niveis[fonte] == 0

    def test_camadas_bfs_por_niveis(self):

        g = _grafo_linear()
        camadas = bfs_por_niveis(g, "A")
        assert camadas[0] == ["A"]
        assert camadas[1] == ["B"]
        assert camadas[2] == ["C"]
        assert camadas[3] == ["D"]

    def test_camadas_estrela(self):

        g = _grafo_estrela()
        camadas = bfs_por_niveis(g, "C")
        assert camadas[0] == ["C"]
        assert set(camadas[1]) == {"F1", "F2", "F3", "F4"}

#testes de ordem de visita
class TestBFSOrdemVisita:

    def test_todos_nos_visitados_grafo_conexo(self):

        g = _grafo_linear()
        ordem, _, _, _ = bfs(g, "A")
        assert set(ordem) == {"A", "B", "C", "D"}

    def test_primeiro_visitado_e_origem(self):

        g = _grafo_estrela()
        ordem, _, _, _ = bfs(g, "C")
        assert ordem[0] == "C"

    def test_bfs_nao_visita_nos_desconexos(self):

        g = _grafo_desconexo()
        ordem, niveis, _, _ = bfs(g, "A")
        assert "X" not in niveis
        assert "Y" not in niveis
        assert set(ordem) == {"A", "B", "C"}

#testes de predecessores/caminho
class TestBFSCaminho:

    def test_caminho_direto(self):

        g = _grafo_linear()
        caminho = bfs_caminho(g, "A", "D")
        assert caminho == ["A", "B", "C", "D"]

    def test_caminho_inacessivel_retorna_none(self):

        g = _grafo_desconexo()
        caminho = bfs_caminho(g, "A", "X")
        assert caminho is None

    def test_caminho_para_si_mesmo(self):

        g = _grafo_linear()
        caminho = bfs_caminho(g, "B", "B")
        assert caminho == ["B"]

    def test_caminho_minimo_em_saltos(self):

        g = _grafo_estrela()
        caminho = bfs_caminho(g, "F1", "F2")
        assert len(caminho) == 3
        assert caminho[0] == "F1"
        assert caminho[-1] == "F2"

    def test_predecessores_consistentes(self):

        g = _grafo_aeroportos_mini()
        _, _, predecessores, _ = bfs(g, "REC")
        nos = g.get_nos()
        for no, pred in predecessores.items():
            if pred is not None:
                assert pred in nos
                vizinhos = g.get_vizinhos(pred)
                assert no in vizinhos


#testes de classificação de arestas
class TestBFSClassificacaoArestas:

    def test_arestas_arvore_cobrem_nos_visitados(self):

        g = _grafo_aeroportos_mini()
        ordem, _, _, arestas_tipo = bfs(g, "REC")
        arvore = [(u, v) for u, v, t in arestas_tipo if t == "arvore"]
        assert len(arvore) == len(ordem) - 1

    def test_grafo_ciclo_tem_aresta_cruzada(self):

        g = _grafo_ciclo()
        _, _, _, arestas_tipo = bfs(g, "A")
        tipos = {t for _, _, t in arestas_tipo}
        assert "cruzada" in tipos

#testes de robustez
class TestBFSRobustez:

    def test_origem_invalida_levanta_erro(self):

        g = _grafo_linear()
        with pytest.raises(ValueError):
            bfs(g, "Z")

    def test_grafo_com_um_no(self):

        g = Grafo()
        g.adicionar_no("SOLO")
        ordem, niveis, predecessores, _ = bfs(g, "SOLO")
        assert ordem == ["SOLO"]
        assert niveis == {"SOLO": 0}
        assert predecessores == {"SOLO": None}