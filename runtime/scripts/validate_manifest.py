
#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

MANIFEST_PATH = (
    Path(__file__).resolve().parents[1] / "manifest.json"
)

REQUIRED_FIELDS = {
    "schema_version",
    "project",
    "runtime_version",
    "platform",
    "status",
    "components",
    "security"
}

COMPONENT_FIELDS = {
    "id",
    "name",
    "version",
    "status",
    "required",
    "download_url",
    "sha256"
}

def validate_manifest(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: Cannot read manifest: {error}")
        return False

    errors = []

    if not isinstance(data, dict):
        print("ERROR: Manifest must be a JSON object.")
        return False

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        errors.append(f"Missing fields: {sorted(missing)}")

    if data.get("schema_version") != 1:
        errors.append("Unsupported schema_version.")

    if data.get("project") != "QTESHAT-GAMING-RUNTIME":
        errors.append("Invalid project identifier.")

    if data.get("status") not in {"development", "stable"}:
        errors.append("Invalid runtime status.")

    components = data.get("components")

    if not isinstance(components, list):
        errors.append("components must be a list.")
        components = []

    seen_ids = set()

    for index, component in enumerate(components):
        if not isinstance(component, dict):
            errors.append(f"Component {index} must be an object.")
            continue

        missing_fields = COMPONENT_FIELDS - component.keys()
        if missing_fields:
            errors.append(
                f"Component {index} missing fields: "
                f"{sorted(missing_fields)}"
            )
            continue

        component_id = component["id"]

        if not isinstance(component_id, str) or not component_id:
            errors.append(f"Component {index} has invalid id.")
            continue

        if component_id in seen_ids:
            errors.append(f"Duplicate component id: {component_id}")

        seen_ids.add(component_id)

        status = component["status"]

        if status not in {"planned", "ready"}:
            errors.append(f"{component_id}: invalid status.")
            continue

        if status == "ready":
            if not component["version"]:
                errors.append(f"{component_id}: missing version.")

            url = component["download_url"]
            if not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{component_id}: invalid HTTPS URL.")

            checksum = component["sha256"]
            if not isinstance(checksum, str) or not re.fullmatch(
                r"[a-fA-F0-9]{64}", checksum
            ):
                errors.append(f"{component_id}: invalid SHA-256.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return False

    print("SUCCESS: Manifest structure is valid.")
    print(f"Components checked: {len(components)}")
    return True


if __name__ == "__main__":
    manifest = Path(sys.argv[1]) if len(sys.argv) > 1 else MANIFEST_PATH
    sys.exit(0 if validate_manifest(manifest) else 1)
