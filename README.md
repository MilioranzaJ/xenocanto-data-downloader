# xenocanto-data-downloader

This repository provides a fully automated pipeline for downloading, organizing, and preparing bird audio recordings from the **Xeno-Canto** platform using its **API 2.0**.  
The goal is to support bioacoustic research, dataset generation for machine learning, and preprocessing tasks for bird sound classification.

## Features
- Fetches recordings from the Xeno-Canto API 2.0
- Supports multiple species at once
- Automatically organizes audio files into folders by species
- Saves metadata for each recording
- Ideal for machine learning and bioacoustics workflows

## Requirements
- Python 3.9+
- `requests`
- `os`
- `time`

Install dependencies:

pip install -r requirements.txt

🔧 How It Works

The script sends HTTP requests to the Xeno-Canto API 2.0, retrieves metadata and audio links, and downloads the .mp3 files into species-specific folders.
All pages of the API results are automatically processed, ensuring full dataset retrieval.

🐦 Credits

All audio data is provided by Xeno-Canto, an open, community-driven bird sound archive.
You can find their platform here: https://xeno-canto.org/

This project uses the Xeno-Canto API 2.0, documented at:
https://xeno-canto.org/article/153
