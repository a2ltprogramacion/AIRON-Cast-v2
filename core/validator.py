"""
AIRON-Cast — Output Validator
==============================
Valida que el output de un agente cumpla con el output_schema definido en manifest.json.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Resultado de la validación de un output de agente."""
    passed: bool
    errors: List[str]


class OutputValidator:
    """Valida output contra el schema en manifest.json."""

    def __init__(self, manifest_path: Path = Path("manifest.json")):
        self.manifest_path = manifest_path
        self._manifest = None
        self._load_manifest()

    def _load_manifest(self) -> None:
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"No se encontró manifest.json en {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self._manifest = json.load(f)

    def _get_schema_for_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        agents = self._manifest.get("agents", {})
        agent = agents.get(agent_name)
        if not agent:
            return None
        return agent.get("output_schema")

    def _validate_against_schema(
        self, value: Any, schema: Dict[str, Any], path: str = ""
    ) -> List[str]:
        errors = []
        expected_type = schema.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"{path}: se esperaba string, se obtuvo {type(value).__name__}")
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"{path}: se esperaba integer, se obtuvo {type(value).__name__}")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            errors.append(f"{path}: se esperaba number, se obtuvo {type(value).__name__}")
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"{path}: se esperaba boolean, se obtuvo {type(value).__name__}")
        elif expected_type == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: se esperaba object, se obtuvo {type(value).__name__}")
            else:
                properties = schema.get("properties", {})
                required = set(schema.get("required", []))
                for prop in required:
                    if prop not in value:
                        errors.append(f"{path}.{prop}: campo requerido ausente")
                for prop, prop_value in value.items():
                    if prop in properties:
                        errors.extend(
                            self._validate_against_schema(prop_value, properties[prop], f"{path}.{prop}")
                        )
        elif expected_type == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: se esperaba array, se obtuvo {type(value).__name__}")
            else:
                items_schema = schema.get("items")
                if items_schema:
                    for i, item in enumerate(value):
                        errors.extend(
                            self._validate_against_schema(item, items_schema, f"{path}[{i}]")
                        )
        return errors

    def validate(self, agent_name: str, output_dict: Dict[str, Any]) -> ValidationResult:
        schema = self._get_schema_for_agent(agent_name)
        if schema is None:
            return ValidationResult(passed=True, errors=[])
        errors = self._validate_against_schema(output_dict, schema, "")
        return ValidationResult(passed=len(errors) == 0, errors=errors)


def validate_output(
    agent_name: str,
    output_dict: Dict[str, Any],
    manifest_path: Path = Path("manifest.json"),
) -> ValidationResult:
    """Wrapper para validar output de agente sin instanciar clase."""
    validator = OutputValidator(manifest_path)
    return validator.validate(agent_name, output_dict)