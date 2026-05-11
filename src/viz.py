"""
viz.py — Parte 8: Explorações e Visualizações Analíticas
Gera 4 visualizações salvas em out/
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

def ler_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ler_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

COR_REGIAO = {
    "Norte":        "#2196F3",
    "Nordeste":     "#FF9800",
    "Centro-Oeste": "#9C27B0",
    "Sudeste":      "#F44336",
    "Sul":          "#4CAF50",
}

# ── VIZ 1: Histograma de distribuição de graus ─────────────────────────────
def viz1_distribuicao_graus():
    graus_raw = ler_csv(os.path.join(OUT, "graus.csv"))
    graus = [int(r["grau"]) for r in graus_raw]

    fig, ax = plt.subplots(figsize=(8, 5))
    bins = range(0, max(graus) + 2)
    counts, edges, patches = ax.hist(graus, bins=bins, align="left",
                                     color="#1565C0", edgecolor="white",
                                     linewidth=0.8, rwidth=0.8)
    max_count = max(counts)
    for patch, count in zip(patches, counts):
        if count == max_count:
            patch.set_facecolor("#FF6F00")

    ax.set_title("Distribuição de Graus dos Aeroportos", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Grau (número de conexões)", fontsize=11)
    ax.set_ylabel("Quantidade de aeroportos", fontsize=11)
    ax.set_xticks(list(bins))
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    media = np.mean(graus)
    ax.axvline(media, color="#E53935", linestyle="--", linewidth=1.5,
               label=f"Média = {media:.1f}")
    ax.legend(fontsize=10)

    fig.text(0.5, -0.04,
        "Insight: A maioria dos aeroportos tem grau baixo (1-2), com poucos hubs centrais.\n"
        "BSB concentra as conexões inter-regionais — padrão típico de rede scale-free.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz1_distribuicao_graus.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

# ── VIZ 2: Ranking de aeroportos (barras horizontais) ─────────────────────
def viz2_ranking_aeroportos():
    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    regiao_map = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    graus_raw = ler_csv(os.path.join(OUT, "graus.csv"))
    graus_raw.sort(key=lambda r: int(r["grau"]), reverse=True)

    labels = [r["aeroporto"] for r in graus_raw]
    values = [int(r["grau"]) for r in graus_raw]
    cores  = [COR_REGIAO.get(regiao_map.get(a, ""), "#888") for a in labels]

    fig, ax = plt.subplots(figsize=(8, 7))
    bars = ax.barh(labels[::-1], values[::-1], color=cores[::-1],
                   edgecolor="white", linewidth=0.6)

    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", ha="left", fontsize=10, fontweight="bold")

    ax.set_title("Ranking de Aeroportos por Conectividade (Grau)", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Grau (número de conexões)", fontsize=11)
    ax.set_ylabel("Aeroporto (código IATA)", fontsize=11)
    ax.set_xlim(0, max(values) + 1.5)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    patches_leg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    ax.legend(handles=patches_leg, title="Região", fontsize=9,
              title_fontsize=9, loc="lower right")

    fig.text(0.5, -0.03,
        "Insight: BSB (grau 6) e GRU/FOR/GIG (grau 4) são os grandes hubs da rede.\n"
        "Aeroportos como RBR, GYN e POA têm grau 1 — dependem completamente de escala.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz2_ranking_aeroportos.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

# ── VIZ 3: Comparação de métricas por região (barras agrupadas) ────────────
def viz3_comparacao_regioes():
    regioes = ler_json(os.path.join(OUT, "regioes.json"))

    nomes    = [r["regiao"]    for r in regioes]
    ordens   = [r["ordem"]     for r in regioes]
    tamanhos = [r["tamanho"]   for r in regioes]
    densids  = [r["densidade"] for r in regioes]

    x = np.arange(len(nomes))
    w = 0.28

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - w, ordens,   w, label="Ordem (|V|)",   color="#1976D2", alpha=0.85)
    b2 = ax1.bar(x,     tamanhos, w, label="Tamanho (|E|)", color="#388E3C", alpha=0.85)
    b3 = ax2.bar(x + w, densids,  w, label="Densidade",     color="#F57C00", alpha=0.85)

    ax1.set_title("Comparação de Métricas por Região", fontsize=14,
                  fontweight="bold", pad=12)
    ax1.set_xlabel("Região", fontsize=11)
    ax1.set_ylabel("Quantidade (|V| e |E|)", fontsize=11)
    ax2.set_ylabel("Densidade", fontsize=11, color="#F57C00")
    ax2.set_ylim(0, 1.4)
    ax2.tick_params(axis="y", colors="#F57C00")
    ax1.set_xticks(x)
    ax1.set_xticklabels(nomes, fontsize=10)
    ax1.yaxis.get_major_locator().set_params(integer=True)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 0.05, str(int(h)),
                 ha="center", va="bottom", fontsize=9)
    for bar in b3:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.02, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=9)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")

    fig.text(0.5, -0.04,
        "Insight: Centro-Oeste tem a maior densidade (1.0) por ser um subgrafo pequeno e completo.\n"
        "Nordeste tem mais nos, mas densidade menor — conexoes poderiam ser expandidas.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz3_comparacao_regioes.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

# ── VIZ 4: Camadas BFS a partir de BSB ────────────────────────────────────
def bfs_camadas(adj, origem):
    visitado = {origem: 0}
    fila = [origem]
    while fila:
        atual = fila.pop(0)
        for vizinho in adj.get(atual, []):
            if vizinho not in visitado:
                visitado[vizinho] = visitado[atual] + 1
                fila.append(vizinho)
    return visitado

def viz4_bfs_camadas():
    adj_raw = ler_csv(os.path.join(DATA, "adjacencias_aeroportos.csv"))
    aeroportos_raw = ler_csv(os.path.join(DATA, "aeroportos_data.csv"))
    regiao_map = {r["iata"]: r["regiao"] for r in aeroportos_raw}

    adj = {}
    for row in adj_raw:
        o, d = row["origem"], row["destino"]
        adj.setdefault(o, []).append(d)
        adj.setdefault(d, []).append(o)

    origem = "BSB"
    niveis = bfs_camadas(adj, origem)

    grupos = {}
    for no, nivel in niveis.items():
        grupos.setdefault(nivel, []).append(no)

    max_nivel = max(grupos.keys())
    n_cols = max(len(v) for v in grupos.values())

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(-0.8, n_cols + 0.8)
    ax.set_ylim(-0.6, max_nivel + 1.0)
    ax.axis("off")

    pos = {}
    for nivel, nos in grupos.items():
        y = max_nivel - nivel
        xs = np.linspace(0.5, n_cols - 0.5, len(nos)) if len(nos) > 1 else [n_cols / 2]
        for no, x in zip(nos, xs):
            pos[no] = (x, y)

    desenhadas = set()
    for row in adj_raw:
        o, d = row["origem"], row["destino"]
        chave = tuple(sorted([o, d]))
        if chave not in desenhadas and o in pos and d in pos:
            desenhadas.add(chave)
            xo, yo = pos[o]
            xd, yd = pos[d]
            ax.plot([xo, xd], [yo, yd], color="#BDBDBD", linewidth=1, zorder=1)

    for no, (x, y) in pos.items():
        regiao = regiao_map.get(no, "")
        cor    = COR_REGIAO.get(regiao, "#888")
        nivel  = niveis[no]
        raio   = 0.38 if nivel == 0 else 0.28
        circulo = plt.Circle((x, y), raio, color=cor, zorder=2, linewidth=1.5,
                             edgecolor="white")
        ax.add_patch(circulo)
        ax.text(x, y, no, ha="center", va="center",
                fontsize=8, fontweight="bold", color="white", zorder=3)

    for nivel in range(max_nivel + 1):
        y = max_nivel - nivel
        label = f"Nível {nivel}" if nivel > 0 else f"Nível {nivel} (origem)"
        ax.text(-0.6, y, label, va="center", ha="right",
                fontsize=9, color="#555", style="italic")
        ax.axhline(y, color="#eee", linestyle="--", linewidth=0.5, zorder=0)

    ax.set_title(f"Camadas BFS a partir de {origem} (Hub Central)", fontsize=14,
                 fontweight="bold")

    patches_leg = [mpatches.Patch(color=c, label=r) for r, c in COR_REGIAO.items()]
    ax.legend(handles=patches_leg, title="Região", fontsize=9,
              title_fontsize=9, loc="upper right")

    fig.text(0.5, -0.02,
        "Insight: BSB alcanca todos os aeroportos em no maximo 4 saltos, confirmando seu papel de hub nacional.\n"
        "Aeroportos de nivel 4 (RBR, POA) sao extremidades da rede — mais vulneraveis a desconexao.",
        ha="center", fontsize=9, style="italic", color="#444")

    plt.tight_layout()
    path = os.path.join(OUT, "viz4_bfs_camadas_BSB.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {path}")

def main():
    print("=== Gerando visualizacoes — Parte 8 ===")
    viz1_distribuicao_graus()
    viz2_ranking_aeroportos()
    viz3_comparacao_regioes()
    viz4_bfs_camadas()
    print("\nPronto! Arquivos salvos em out/")

if __name__ == "__main__":
    main()