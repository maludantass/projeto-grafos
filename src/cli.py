import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from graphs.io import ler_aeroportos, ler_adjacencias

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivo_csv_nos = os.path.join(base_dir, "data", "aeroportos_data.csv")
    arquivo_csv_arestas = os.path.join(base_dir, "data", "adjacencias_aeroportos.csv")
    
    print(f"Lendo arquivo de aeroportos: {arquivo_csv_nos}")
    try:
        grafo = ler_aeroportos(arquivo_csv_nos)
        
        print(f"Lendo arquivo de adjacências: {arquivo_csv_arestas}")
        ler_adjacencias(grafo, arquivo_csv_arestas)
        
        print("\nInformações do Grafo")
        print(grafo)
        
        print("\nNós Adicionados")
        nos = grafo.get_nos()
        print(f"Total: {len(nos)} nós")
        print(nos)
        
        print("\nExemplo de Arestas Adicionadas")
        for iata in nos[:3]: # Mostrando arestas dos 3 primeiros nós
            vizinhos = grafo.adj_list.get(iata, [])
            print(f"Aeroporto {iata} conectado com: ")
            for v in vizinhos:
                print(f"  - {v['vizinho']} (Peso: {v['peso']}, Tipo: {v['tipo_conexao']}, Justificativa: '{v['justificativa']}')")
            
    except FileNotFoundError as e:
        print(f"Erro de arquivo não encontrado: {e}")

if __name__ == "__main__":
    main()
