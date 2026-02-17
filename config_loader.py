import json
import os
from logger import logger

DEFAULT_CONFIG = {
    "excel_file": "data.xlsx",
    "refresh_interval": 2,
    "serial": {
        "port": "COM3",
        "baudrate": 9600,
        "parity": "N",
        "stopbits": 1,
        "bytesize": 8,
        "slave_id": 1
    },
    "register_map": []
}

class ConfigLoader:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()

    def load_config(self):
        """Loads and validates the configuration from the JSON file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file {self.config_path} not found. Creating default.")
            self.save_config()
            return self.config

        try:
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)
                # Basic validation: update default with loaded values to ensure keys exist
                self._update_recursive(self.config, loaded_config)
            logger.info("Configuration loaded successfully.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON config: {e}. Using defaults.")
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}. Using defaults.")

        return self.config

    def _update_recursive(self, base_dict, update_dict):
        for k, v in update_dict.items():
            if isinstance(v, dict) and k in base_dict:
                self._update_recursive(base_dict[k], v)
            else:
                base_dict[k] = v

    def save_config(self):
        """Saves current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

# Global instance
config_loader = ConfigLoader()
