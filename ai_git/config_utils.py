"""Utility functions for configuration handling."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnknownModelAliasError(Exception):
    """Exception raised when an unknown model alias is encountered."""
    def __init__(self, alias: str, known_aliases: Dict[str, str]):
        self.alias = alias
        self.known_aliases = known_aliases
        super().__init__(f"Unknown model alias: '{alias}'")

def resolve_model_alias(model_name: str, raise_on_unknown: bool = False) -> str:
    """
    Resolve a model alias to its full identifier.
    
    If the model name contains a slash ('/'), it's assumed to be a full identifier
    and is returned as is. Otherwise, it's treated as an alias and looked up in
    the config/model-aliases.yaml file.
    
    Args:
        model_name: The model name or alias to resolve
        
    Returns:
        The resolved full model identifier, or the original model_name if:
        - It already contains a slash ('/')
        - The config file doesn't exist
        - The config file can't be parsed
        - The alias isn't found in the config
    """
    # If model_name already contains a slash, it's a full identifier
    if '/' in model_name:
        return model_name
    
    # Get the project root directory
    # Assuming this file is in ai_git/ which is at the project root
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "model-aliases.yaml"
    
    try:
        # Check if the config file exists
        if not config_path.exists():
            logger.warning(f"Model aliases config file not found: {config_path}")
            return model_name
        
        # Load the aliases from the YAML file
        with open(config_path, 'r') as f:
            aliases = yaml.safe_load(f)
            
        # Check if the loaded content is a dictionary
        if not isinstance(aliases, dict):
            logger.warning(f"Invalid format in model aliases config: {config_path}")
            return model_name
            
        # Look up the alias
        if model_name in aliases:
            resolved_model = aliases[model_name]
            logger.info(f"Resolved model alias '{model_name}' to '{resolved_model}'")
            return resolved_model
        else:
            logger.warning(f"Unknown model alias: '{model_name}'")
            if raise_on_unknown:
                raise UnknownModelAliasError(model_name, aliases)
            return model_name
            
    except yaml.YAMLError as e:
        logger.error(f"Error parsing model aliases config: {e}")
        return model_name
    except UnknownModelAliasError:
        # Re-raise UnknownModelAliasError to be handled by the caller
        raise
    except Exception as e:
        logger.error(f"Unexpected error resolving model alias: {e}")
        return model_name
        
def get_available_aliases() -> Dict[str, str]:
    """
    Get a dictionary of available model aliases from the config file.
    
    Returns:
        A dictionary mapping aliases to their full model identifiers.
        Empty dictionary if the config file doesn't exist or can't be parsed.
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "model-aliases.yaml"
    
    try:
        # Check if the config file exists
        if not config_path.exists():
            logger.warning(f"Model aliases config file not found: {config_path}")
            return {}
        
        # Load the aliases from the YAML file
        with open(config_path, 'r') as f:
            aliases = yaml.safe_load(f)
            
        # Check if the loaded content is a dictionary
        if not isinstance(aliases, dict):
            logger.warning(f"Invalid format in model aliases config: {config_path}")
            return {}
            
        return aliases
            
    except yaml.YAMLError as e:
        logger.error(f"Error parsing model aliases config: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error getting available aliases: {e}")
        return {}