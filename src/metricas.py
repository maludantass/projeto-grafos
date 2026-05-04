"""
Parte 3 - Métricas Globais e por Grupo
"""
import os
import sys
import json
import csv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias


def calcular_densidade(num_nos, num_arestas):
    if num_nos < 2:
        return 0.0
    return (2 * num_arestas) / (num_nos * (num_nos - 1))


def metricas_subgrafo(grafo, nos_subset):
    nos_set = set(nos_subset)
    ordem = len(nos_set)
    arestas = 0
    for no in nos_set:
        for aresta in grafo.adj_list.get(no, []):
            if aresta['vizinho'] in nos_set:
                arestas += 1
    tamanho = arestas // 2
    densidade = calcular_densidade(ordem, tamanho)
    return ordem, tamanho, round(densidade, 6)


def grau_no(grafo, no):
    return len(grafo.adj_list.get(no, []))


def ego_network(grafo, no):
    vizinhos = [a['vizinho'] for a in grafo.adj_list.get(no, [])]
    return list(set([no] + vizinhos))


def calcular_metricas_globais(grafo):
    nos = grafo.get_nos()
    ordem = len(nos)
    tamanho = sum(len(v) for v in grafo.adj_list.values()) // 2
    densidade = calcular_densidade(ordem, tamanho)
    return {
        "ordem": ordem,
        "tamanho": tamanho,
        "densidade": round(densidade, 6)
    }


def calcular_metricas_regioes(grafo):
    regioes = {}
    for no in grafo.get_nos():
        attrs = grafo.get_atributos_no(no)
        regiao = attrs.get('regiao', 'Desconhecida') if attrs else 'Desconhecida'
        regioes.setdefault(regiao, []).append(no)

    resultado = []
    for regiao, nos in sorted(regioes.items()):
        ordem, tamanho, densidade = metricas_subgrafo(grafo, nos)
        resultado.append({
            "regiao": regiao,
            "nos": sorted(nos),
            "ordem": ordem,
            "tamanho": tamanho,
            "densidade": densidade
        })
    return resultado


def calcular_ego_aeroportos(grafo):
    resultado = []
    for no in sorted(grafo.get_nos()):
        grau = grau_no(grafo, no)
        nos_ego = ego_network(grafo, no)
        ordem_ego, tamanho_ego, densidade_ego = metricas_subgrafo(grafo, nos_ego)
        resultado.append({
            "aeroporto": no,
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": densidade_ego
        })
    return resultado


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_nos    = os.path.join(base_dir, "data", "aeroportos_data.csv")
    arquivo_arestas = os.path.join(base_dir, "data", "adjacencias_aeroportos.csv")
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)

    print("Carregando grafo...")
    grafo = ler_aeroportos(arquivo_nos)
    ler_adjacencias(grafo, arquivo_arestas)
    print(grafo)

    print("\nCalculando métricas...")
    global_m  = calcular_metricas_globais(grafo)
    regioes_m = calcular_metricas_regioes(grafo)
    ego_m     = calcular_ego_aeroportos(grafo)

    # Imprime no terminal
    print("\n" + "="*60)
    print("PARTE 3 — MÉTRICAS GLOBAIS E POR GRUPO")
    print("="*60)

    print(f"\n[1] Grafo Completo")
    print(f"    Ordem   : {global_m['ordem']} nós")
    print(f"    Tamanho : {global_m['tamanho']} arestas")
    print(f"    Densidade: {global_m['densidade']:.6f}")

    print(f"\n[2] Subgrafos por Região")
    print(f"  {'Região':<15} {'Ordem':>6} {'Tamanho':>8} {'Densidade':>10}")
    print(f"  {'-'*15} {'-'*6} {'-'*8} {'-'*10}")
    for r in regioes_m:
        print(f"  {r['regiao']:<15} {r['ordem']:>6} {r['tamanho']:>8} {r['densidade']:>10.6f}")

    print(f"\n[3] Ego-Subrede por Aeroporto")
    print(f"  {'Aeroporto':<12} {'Grau':>5} {'Ord.Ego':>8} {'Tam.Ego':>8} {'Dens.Ego':>10}")
    print(f"  {'-'*12} {'-'*5} {'-'*8} {'-'*8} {'-'*10}")
    for e in ego_m:
        print(f"  {e['aeroporto']:<12} {e['grau']:>5} {e['ordem_ego']:>8} {e['tamanho_ego']:>8} {e['densidade_ego']:>10.6f}")

    # Salva os arquivos
    print("\nSalvando arquivos...")
    with open(os.path.join(out_dir, "global.json"), 'w', encoding='utf-8') as f:
        json.dump(global_m, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "regioes.json"), 'w', encoding='utf-8') as f:
        json.dump(regioes_m, f, ensure_ascii=False, indent=2)

    campos = ["aeroporto", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
    with open(os.path.join(out_dir, "ego_aeroportos.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(ego_m)

    print("Concluído! Arquivos salvos em out/")


if __name__ == "__main__":
    main()