import requests
import time
import os
import csv
import folium 
from collections import defaultdict

API_KEY = "api aqui"

BASE_FOLDER = "pantanal_completo_xeno_canto"
AUDIO_FOLDER = os.path.join(BASE_FOLDER, "audios")
CSV_FILENAME = os.path.join(BASE_FOLDER, "relatorio_pantanal.csv")
MAP_FILENAME = os.path.join(BASE_FOLDER, "mapa_visualizacao.html")

BOX_COORDS = "-22.5,-59.5,-15.5,-54.5"

MAX_DOWNLOADS_PER_SPECIES = 5
ONLY_HIGH_QUALITY = False

def get_quality_score(quality_char):
    mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    return mapping.get(quality_char, 99)

def gerar_mapa(box_string, output_path):
    """Gera um arquivo HTML com o mapa da área selecionada"""
    print(f"🗺️  Gerando mapa de visualização...")
    try:
        lat_min, lon_min, lat_max, lon_max = map(float, box_string.split(','))

        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        folium.Rectangle(
            bounds=[[lat_min, lon_min], [lat_max, lon_max]],
            color="red", fill=True, fill_opacity=0.1,
            popup="Área de Coleta (Pantanal)"
        ).add_to(m)
        
        m.save(output_path)
        print(f"Mapa salvo em: {output_path}")
    except Exception as e:
        print(f"⚠️ Erro ao gerar mapa: {e}")

def main():
    if API_KEY == "SUA_CHAVE_API_VAI_AQUI" or not API_KEY:
        print("ERRO: Configura a API_KEY no script.")
        return

    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    
    gerar_mapa(BOX_COORDS, MAP_FILENAME)
    
    query = f"box:{BOX_COORDS}"
    base_url = "https://xeno-canto.org/api/3/recordings"
    
    print(f"\n--- INICIANDO VARREDURA (PANTANAL INTEIRO) ---")
    print("Coletando metadados...")

    all_metadata = []
    page = 1
    total_pages = 1 
    
    while page <= total_pages:
        try:
            params = {"query": query, "key": API_KEY, "page": page}
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if page == 1:
                total_pages = int(data.get("numPages", 1))
                total_recordings = int(data.get("numRecordings", 0))
                print(f"-> Total encontrado: {total_recordings} gravações")
                
                if total_recordings == 0:
                    print("⚠️ Nenhuma gravação encontrada.")
                    return

            print(f"Lendo página {page}/{total_pages}...", end='\r')
            
            recordings = data.get("recordings", [])
            all_metadata.extend(recordings)
            
            page += 1
            time.sleep(0.5) 
            
        except Exception as e:
            print(f"\nrro na página {page}: {e}")
            break

    print(f"\nLeitura concluída! {len(all_metadata)} registros.")

    print(f"\n--- GERANDO CSV ---")
    species_map = defaultdict(list)
    
    for rec in all_metadata:
        gen = rec.get('gen', '').strip()
        sp = rec.get('sp', '').strip()
        full_name = f"{gen} {sp}"
        species_map[full_name].append(rec)

    try:
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Especie', 'Nome_Comum', 'Qtd_Gravacoes', 'Paises']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            sorted_species = sorted(species_map.items(), key=lambda item: len(item[1]), reverse=True)
            
            for sp_name, rec_list in sorted_species:
                common_name = rec_list[0].get('en', 'Unknown')
                paises = sorted(list(set([r.get('cnt') for r in rec_list if r.get('cnt')])))
                
                writer.writerow({
                    'Especie': sp_name,
                    'Nome_Comum': common_name,
                    'Qtd_Gravacoes': len(rec_list),
                    'Paises': ", ".join(paises)
                })
        print(f"CSV salvo em: {CSV_FILENAME}")
    except Exception as e:
        print(f"Erro no CSV: {e}")

    print(f"\n--- INICIANDO DOWNLOADS (Top {MAX_DOWNLOADS_PER_SPECIES}) ---")
    
    total_downloaded = 0
    
    for sp_name, rec_list in species_map.items():
        rec_list.sort(key=lambda x: get_quality_score(x.get('q', 'E')))
        top_recordings = rec_list[:MAX_DOWNLOADS_PER_SPECIES]
        
        safe_folder_name = sp_name.replace(" ", "_").replace("/", "-")
        sp_folder_path = os.path.join(AUDIO_FOLDER, safe_folder_name)
        os.makedirs(sp_folder_path, exist_ok=True)
        
        count_sp = 0
        for rec in top_recordings:
            if ONLY_HIGH_QUALITY and rec.get('q') != 'A': continue

            file_url = rec.get("file")
            file_name = rec.get("file-name")
            
            if not file_url or not file_name: continue
                
            file_path = os.path.join(sp_folder_path, file_name)
            
            if os.path.exists(file_path): continue
            
            try:
                if count_sp == 0: print(f"Processando: {sp_name}...")
                
                r = requests.get(file_url, stream=True)
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                count_sp += 1
                total_downloaded += 1
            except:
                pass
        
        if count_sp > 0: time.sleep(0.2)

    print("\nPROCESSO CONCLUÍDO!")
    print(f"Arquivos em: {BASE_FOLDER}")

if __name__ == "__main__":
    main()