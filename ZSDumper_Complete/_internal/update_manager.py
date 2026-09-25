import json
import os
import sys
import requests
import urllib.request
import urllib.error
import threading
from pathlib import Path
from typing import Optional, Tuple

class UpdateManager:
    def __init__(self, config_file="zsdumper_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.current_version = self.config.get('version', '2.0')
        self.api_url = self.config.get('api', {}).get('url', 'https://api-zsdump.zinz1-dev.fr')
        
    def load_config(self) -> dict:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            "version": "2.0",
            "api": {"url": "https://api-zsdump.zinz1-dev.fr"}
        }
        
    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check for updates via API.
        Returns: (has_update, latest_version, download_url)
        """
        try:
            response = requests.get(
                f"{self.api_url}/version",
                timeout=10,
                headers={'User-Agent': 'ZSDumper/2.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('version', self.current_version)
                download_url = data.get('download_url')
                
                if latest_version != self.current_version:
                    return True, latest_version, download_url
                    
            return False, self.current_version, None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API: {e}")
            return False, self.current_version, None
        except json.JSONDecodeError:
            print("Erreur: réponse API invalide")
            return False, self.current_version, None
        except Exception as e:
            print(f"Erreur lors de la vérification: {e}")
            return False, self.current_version, None
            
    def download_update(self, download_url: str, progress_callback=None) -> bool:
        """
        Download update from the provided URL.
        Returns: True if successful, False otherwise
        """
        try:
            # Create temp directory for download
            temp_dir = Path("Temp_Updates")
            temp_dir.mkdir(exist_ok=True)
            
            update_file = temp_dir / "ZSDumper_Update.exe"
            
            def download_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = (block_num * block_size / total_size) * 100
                    progress_callback(min(percent, 100))
            
            urllib.request.urlretrieve(
                download_url,
                update_file,
                reporthook=download_progress
            )
            
            return True
            
        except urllib.error.URLError as e:
            print(f"Erreur de téléchargement: {e}")
            return False
        except Exception as e:
            print(f"Erreur lors du téléchargement: {e}")
            return False
            
    def install_update(self, update_file: str) -> bool:
        """
        Install the downloaded update.
        This creates a batch script to replace the current executable.
        """
        try:
            # Create a batch script to handle the update after the app closes
            script_path = Path("ZSDumper_Update.bat")
            
            script_content = f"""@echo off
timeout /t 2 /nobreak >nul
move /Y "{update_file}" "ZSDumper.exe"
start "" "ZSDumper.exe"
del "{script_path}"
"""
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Launch the script and exit the app
            import subprocess
            subprocess.Popen(script_path, shell=True)
            sys.exit(0)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'installation: {e}")
            return False
            
    def get_changelog(self, version: str) -> Optional[str]:
        """
        Get changelog for a specific version.
        """
        try:
            response = requests.get(
                f"{self.api_url}/changelog",
                params={'version': version},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('changelog', 'Pas de notes de version disponibles.')
                
        except:
            pass
            
        return None

# Standalone test function
if __name__ == "__main__":
    manager = UpdateManager()
    has_update, version, url = manager.check_for_updates()
    
    if has_update:
        print(f"Mise à jour disponible: {version}")
        print(f"URL de téléchargement: {url}")
    else:
        print(f"ZSDumper est à jour (version {manager.current_version})")
