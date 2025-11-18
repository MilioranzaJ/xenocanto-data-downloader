import requests
import time
import os

api_key = "sua_chave_api_vai_aqui"  # Insira sua chave de API aqui

dataset_folder = "gravacoes_xeno_canto"
country_tag = "cnt:brazil"

#species list example
species_list = [
    {"genus": "turdus", "species": "rufiventris"},    
    {"genus": "pitangus", "species": "sulphuratus"},  
    {"genus": "guira", "species": "guira"},          
]

BASE_URL = "https://xeno-canto.org/api/3/recordings"

def download_species_data(species_info, api_key, country_filter):
    genus = species_info["genus"]
    species = species_info["species"]
    
    species_folder_name = f"{genus.capitalize()}_{species.capitalize()}"
    download_path = os.path.join(dataset_folder, species_folder_name)
    os.makedirs(download_path, exist_ok=True)
    
    query_parts = [f"gen:{genus}", f"sp:{species}"]
    if country_filter:
        query_parts.append(country_filter)
    query = " ".join(query_parts)
    
    print(f"\n--- Iniciando busca para: {species_folder_name} ---")
    print(f"Consulta: '{query}'")

    try:
        params = {"query": query, "key": api_key, "page": 1}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        total_pages = int(data.get("numPages", 1))
        total_recordings = int(data.get("numRecordings", 0))

        if total_recordings == 0:
            print(f"A consulta para '{query}' não retornou resultados. Pulando.")
            return

        print(f"Total de gravações encontradas: {total_recordings}")
        print(f"Total de páginas: {total_pages}")

        all_recordings = []
        
        for page in range(1, total_pages + 1):
            print(f"Coletando dados da página {page} de {total_pages}...")
            params["page"] = page
            page_response = requests.get(BASE_URL, params=params)
            page_response.raise_for_status()
            page_data = page_response.json()
            all_recordings.extend(page_data.get("recordings", []))
            time.sleep(1) 

        print(f"\nIniciando downloads para '{species_folder_name}'...")
        total_baixado = 0
        
        for rec in all_recordings:
            
            file_url = rec.get("file") 
            file_name = rec.get("file-name")
            
            if not file_url or not file_name:
                print(f"AVISO: Gravação ID {rec.get('id')} com dados incompletos, pulando.")
                continue
            
            file_path = os.path.join(download_path, file_name) 
            
            if os.path.exists(file_path):
                print(f"Arquivo já existe: {file_name} (Pulando)")
            else:
                print(f"Baixando: {file_name}...")
                try:
                    audio_response = requests.get(file_url, stream=True)
                    audio_response.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in audio_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    total_baixado += 1
                except requests.exceptions.RequestException as e:
                    print(f"ERRO ao baixar {file_name}: {e}")
        
        print(f"--- {species_folder_name} concluído. {total_baixado} arquivos baixados. ---")

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP para {species_folder_name}: {http_err}")
        if 'response' in locals():
            print(f"Resposta da API: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Erro na requisição para {species_folder_name}: {err}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu para {species_folder_name}: {e}")

def main():
    if api_key == "SUA_CHAVE_API_VAI_AQUI" or api_key == "":
        print("ERRO: Por favor, edite o script e insira sua chave de API na variável 'api_key'.")
        print("Você pode encontrar sua chave em: https://xeno-canto.org/account")
        return

    os.makedirs(dataset_folder, exist_ok=True)
    print(f"Pasta base de downloads: '{dataset_folder}'")

    for species in species_list:
        download_species_data(species, api_key, country_tag)

    print("\n\nProcesso de download de todas as espécies foi concluído.")

if __name__ == "__main__":
    main()