import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graphs.graph import Grafo
from src.graphs.algorithms import dfs, dfs_detectar_ciclo, dfs_componentes_conexos


def _grafo_linear():

    g = Grafo()
    for no in ["A", "B", "C", "D"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("C", "D")
    return g


def _grafo_ciclo_triangulo():

    g = Grafo()
    for no in ["A", "B", "C"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("C", "A")
    return g


def _grafo_desconexo_dois_componentes():

    g = Grafo()
    for no in ["A", "B", "C", "X", "Y", "Z"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("X", "Y")
    g.adicionar_aresta("Y", "Z")
    return g


def _grafo_arvore():

    g = Grafo()
    for no in ["R", "A", "B", "C", "D"]:
        g.adicionar_no(no)
    g.adicionar_aresta("R", "A")
    g.adicionar_aresta("R", "B")
    g.adicionar_aresta("A", "C")
    g.adicionar_aresta("A", "D")
    return g


def _grafo_com_ciclo_extra():

    g = Grafo()
    for no in ["A", "B", "C", "D", "E"]:
        g.adicionar_no(no)
    g.adicionar_aresta("A", "B")
    g.adicionar_aresta("B", "C")
    g.adicionar_aresta("C", "A")
    g.adicionar_aresta("C", "D")
    g.adicionar_aresta("D", "E")
    g.adicionar_aresta("E", "C")
    return g


#testes de ordem de visita
class TestDFSOrdemVisita:

    def test_todos_nos_visitados_grafo_conexo(self):

        g = _grafo_linear()
        ordem, _, _, _, _, _ = dfs(g, "A")
        assert set(ordem) == {"A", "B", "C", "D"}

    def test_primeiro_no_e_a_origem(self):

        g = _grafo_arvore()
        ordem, _, _, _, _, _ = dfs(g, "R")
        assert ordem[0] == "R"

    def test_dfs_visita_todos_em_grafo_desconexo(self):

        g = _grafo_desconexo_dois_componentes()
        ordem, _, _, _, _, _ = dfs(g, "A")
        assert set(ordem) == {"A", "B", "C", "X", "Y", "Z"}

#testes de detecção de ciclo
class TestDFSDeteccaoCiclo:

    def test_grafo_sem_ciclo_retorna_false(self):

        g = _grafo_linear()
        _, _, _, _, _, tem_ciclo = dfs(g, "A")
        assert tem_ciclo is False

    def test_arvore_sem_ciclo_retorna_false(self):

        g = _grafo_arvore()
        _, _, _, _, _, tem_ciclo = dfs(g, "R")
        assert tem_ciclo is False

    def test_triangulo_tem_ciclo(self):

        g = _grafo_ciclo_triangulo()
        _, _, _, _, _, tem_ciclo = dfs(g, "A")
        assert tem_ciclo is True

    def test_grafo_com_dois_ciclos_detecta_ciclo(self):

        g = _grafo_com_ciclo_extra()
        _, _, _, _, _, tem_ciclo = dfs(g, "A")
        assert tem_ciclo is True

    def test_helper_detectar_ciclo_sem_ciclo(self):

        g = _grafo_linear()
        assert dfs_detectar_ciclo(g) is False

    def test_helper_detectar_ciclo_com_ciclo(self):

        g = _grafo_ciclo_triangulo()
        assert dfs_detectar_ciclo(g) is True

#testes de classificação de arestas
class TestDFSClassificacaoArestas:

    def test_arvore_so_tem_arestas_de_arvore(self):

        g = _grafo_arvore()
        _, _, _, _, arestas_tipo, _ = dfs(g, "R")
        vistas = set()
        tipos  = set()
        for u, v, t in arestas_tipo:
            chave = (min(u, v), max(u, v))
            if chave not in vistas:
                vistas.add(chave)
                tipos.add(t)
        assert tipos == {"arvore"}

    def test_grafo_ciclo_tem_aresta_retorno(self):

        g = _grafo_ciclo_triangulo()
        _, _, _, _, arestas_tipo, _ = dfs(g, "A")
        tipos = {t for _, _, t in arestas_tipo}
        assert "retorno" in tipos

    def test_arestas_arvore_cobrem_todos_nos_visitados(self):

        g = _grafo_arvore()
        ordem, _, _, _, arestas_tipo, _ = dfs(g, "R")
        vistas = set()
        arvore = []
        for u, v, t in arestas_tipo:
            chave = (min(u, v), max(u, v))
            if chave not in vistas and t == "arvore":
                vistas.add(chave)
                arvore.append((u, v))
        assert len(arvore) == len(ordem) - 1

#testes de tempos de entrada/saída
class TestDFSTempos:

    def test_tempos_entrada_saida_existem_para_todos_nos(self):

        g = _grafo_linear()
        ordem, _, t_entrada, t_saida, _, _ = dfs(g, "A")
        for no in ordem:
            assert no in t_entrada
            assert no in t_saida

    def test_tempo_entrada_menor_que_saida(self):

        g = _grafo_arvore()
        _, _, t_entrada, t_saida, _, _ = dfs(g, "R")
        for no in t_entrada:
            assert t_entrada[no] < t_saida[no], (
                f"Nó {no}: entrada={t_entrada[no]} >= saida={t_saida[no]}"
            )

    def test_tempos_sao_unicos(self):

        g = _grafo_arvore()
        _, _, t_entrada, t_saida, _, _ = dfs(g, "R")
        todos = list(t_entrada.values()) + list(t_saida.values())
        assert len(todos) == len(set(todos)), "Tempos duplicados encontrados"

    def test_ancestral_tem_entrada_menor(self):

        g = _grafo_arvore()
        _, predecessores, t_entrada, _, _, _ = dfs(g, "R")
        for no, pred in predecessores.items():
            if pred is not None:
                assert t_entrada[pred] < t_entrada[no]

#testes de componentes conexos
class TestDFSComponentes:

    def test_grafo_conexo_tem_um_componente(self):

        g = _grafo_linear()
        componentes = dfs_componentes_conexos(g)
        assert len(componentes) == 1
        assert set(componentes[0]) == {"A", "B", "C", "D"}

    def test_grafo_desconexo_tem_dois_componentes(self):

        g = _grafo_desconexo_dois_componentes()
        componentes = dfs_componentes_conexos(g)
        assert len(componentes) == 2
        nos_por_comp = [set(c) for c in componentes]
        assert {"A", "B", "C"} in nos_por_comp
        assert {"X", "Y", "Z"} in nos_por_comp

    def test_nos_isolados_sao_componentes(self):

        g = Grafo()
        for no in ["P", "Q", "R"]:
            g.adicionar_no(no)
        componentes = dfs_componentes_conexos(g)
        assert len(componentes) == 3

#testes de robustez
class TestDFSRobustez:

    def test_origem_invalida_levanta_erro(self):

        g = _grafo_linear()
        with pytest.raises(ValueError):
            dfs(g, "Z")

    def test_grafo_com_um_no(self):

        g = Grafo()
        g.adicionar_no("SOLO")
        ordem, predecessores, t_e, t_s, arestas, ciclo = dfs(g, "SOLO")
        assert ordem == ["SOLO"]
        assert ciclo is False
        assert arestas == []