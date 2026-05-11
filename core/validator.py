import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Resultado de la validación de un output de agente."""
    passed: bool
    errors: List[str]


class OutputValidator:
    """
    Valida que el output de un agente cumpla con el output_schema definido
    en manifest.json.
    """

    def __init__(self, manifest_path: Path = Path("manifest.json")):
        """
        Inicializa el validador cargando el archivo manifest.json.

        Args:
            manifest_path: Ruta al archivo manifest.json (relativa a la raíz del proyecto).
        """
        self.manifest_path = manifest_path
        self._manifest = None
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Carga el contenido de manifest.json."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"No se encontró manifest.json en {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self._manifest = json.load(f)

    def _get_schema_for_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Extrae el output_schema del agente desde manifest.json.
        Asume estructura: agents[agent_name].output_schema
        """
        agents = self._manifest.get("agents", {})
        agent = agents.get(agent_name)
        if not agent:
            return None
        return agent.get("output_schema")

    def _validate_against_schema(
        self, value: Any, schema: Dict[str, Any], path: str = ""
    ) -> List[str]:
        """
        Valida recursivamente un valor contra un schema simplificado tipo JSON Schema.
        Soporta tipos: string, integer, number, boolean, object, array.
        """
        errors = []
        expected_type = schema.get("type")
        if expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"{path}: se esperaba string, se obtuvo {type(value).__name__}")
        elif expected_type == "integer":
            if not isinstance(value, int):
                errors.append(f"{path}: se esperaba integer, se obtuvo {type(value).__name__}")
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"{path}: se esperaba number, se obtuvo {type(value).__name__}")
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                errors.append(f"{path}: se esperaba boolean, se obtuvo {type(value).__name__}")
        elif expected_type == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: se esperaba object, se obtuvo {type(value).__name__}")
            else:
                properties = schema.get("properties", {})
                required = set(schema.get("required", []))
                # Verificar que todas las propiedades requeridas existan
                for prop in required:
                    if prop not in value:
                        errors.append(f"{path}.{prop}: campo requerido ausente")
                # Validar cada propiedad presente contra su sub-schema
                for prop, prop_value in value.items():
                    if prop in properties:
                        sub_schema = properties[prop]
                        sub_errors = self._validate_against_schema(
                            prop_value, sub_schema, f"{path}.{prop}"
                        )
                        errors.extend(sub_errors)
                    # Si la propiedad no está en el schema, no se valida (se ignora)
        elif expected_type == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: se esperaba array, se obtuvo {type(value).__name__}")
            else:
                items_schema = schema.get("items")
                if items_schema:
                    for i, item in enumerate(value):
                        sub_errors = self._validate_against_schema(
                            item, items_schema, f"{path}[{i}]"
                        )
                        errors.extend(sub_errors)
        else:
            # Tipo desconocido, se omite (no validar)
            pass
        return errors

    def validate(self, agent_name: str, output_dict: Dict[str, Any]) -> ValidationResult:
        """
        Valida el output de un agente.

        Args:
            agent_name: Nombre del agente (debe existir en manifest.json).
            output_dict: Diccionario con el output generado.

        Returns:
            ValidationResult con el resultado de la validación.
        """
        schema = self._get_schema_for_agent(agent_name)
        if schema is None:
            # Si no hay schema definido, se considera válido (no validación)
            return ValidationResult(passed=True, errors=[])

        errors = self._validate_against_schema(output_dict, schema, "")
        return ValidationResult(passed=len(errors) == 0, errors=errors)


# Función de conveniencia
def validate_output(
    agent_name: str,
    output_dict: Dict[str, Any],
    manifest_path: Path = Path("manifest.json"),
) -> ValidationResult:
    """Wrapper para validar output de agente sin instanciar clase."""
    validator = OutputValidator(manifest_path)
    return validator.validate(agent_name, output_dict)


if __name__ == "__main__":
    # Prueba con ejemplo ficticio
    import tempfile

    # Crear un manifest.json temporal para prueba
    manifest_content = {
        "agents": {
            "frontend": {
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "artifact": {"type": "string"},
                        "files": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["artifact", "files"],
                }
            },
            "qa": {
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "qa_report": {"type": "string"},
                        "approved_for_delivery": {"type": "boolean"},
                    },
                    "required": ["qa_report", "approved_for_delivery"],
                }
            },
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(manifest_content, f)
        manifest_path = Path(f.name)

    validator = OutputValidator(manifest_path)

    # Caso 1: output correcto de frontend
    correct_output = {"artifact": "main.js", "files": ["main.js", "styles.css"]}
    result = validator.validate("frontend", correct_output)
    print("Caso correcto frontend:", result.passed, result.errors)
    assert result.passed

    # Caso 2: output con campo faltante
    missing_output = {"artifact": "main.js"}
    result = validator.validate("frontend", missing_output)
    print("Caso faltante frontend:", result.passed, result.errors)
    assert not result.passed
    assert any("campo requerido ausente" in e for e in result.errors)

    # Caso 3: output de QA con approved_for_delivery=False (debe pasar)
    qa_output = {"qa_report": "report.md", "approved_for_delivery": False}
    result = validator.validate("qa", qa_output)
    print("Caso QA con False:", result.passed, result.errors)
    assert result.passed

    # Limpiar
    manifest_path.unlink()