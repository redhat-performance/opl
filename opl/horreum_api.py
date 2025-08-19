#!/usr/bin/env python3
"""
Horreum API Integration Script for Performance Test

This script creates a comprehensive Horreum test and schema setup for performance monitoring.
It uses configuration-driven field definitions from a YAML configuration file and creates labels,
change detection variables, and proper grouping for performance regression monitoring.

Features:
- Loads field definitions from configurable YAML file (default: horreum_fields_config.yaml)
- Creates Horreum test and schema from configuration
- Creates labels with intelligent naming (camelCase + __ prefix)
- Creates change detection variables with smart grouping
- Prevents duplicate labels and variables
- Optional cleanup of obsolete labels and variables
- Dry-run mode for safe preview of all operations including cleanup
- Provides detailed status reporting
- Fully automated operation (no user prompts)
- Flexible configuration file input via command line or environment variable

Authentication:
    API Key (Recommended):
        export HORREUM_API_KEY="HUSR_00000000_0000_0000_0000_000000000000"

    Token (Legacy):
        export HORREUM_TOKEN="your-bearer-token"

Configuration:
    Test and schema definitions are loaded from a YAML configuration file:
    - test: Test configuration (name, owner, description, etc.)
    - schema: Schema configuration (name, URI, owner, etc.)
    - fields: Field definitions with change detection settings
    Default configuration file: horreum_fields_config.yaml

Environment Variables:
    Required:
        HORREUM_URL              - Horreum instance URL
        HORREUM_API_KEY          - API key for authentication

    Optional:
        HORREUM_CONFIG_FILE      - Path to configuration file (default: horreum_fields_config.yaml)
        HORREUM_SCHEMA_ID        - Use existing schema ID (skip creation)
        HORREUM_TEST_ID          - Use existing test ID (skip creation)
        SKIP_LABELS=true         - Skip label creation
        CLEANUP_LABELS=false     - Disable removal of obsolete labels (default: enabled)
        CLEANUP_VARIABLES=false  - Disable removal of obsolete variables (default: enabled)
        DRY_RUN=false           - Execute changes (default: dry run enabled)

Command Line Arguments:
    --config-file, -c           - Path to configuration file (overrides HORREUM_CONFIG_FILE)

Usage:
    # Basic usage (uses horreum_fields_config.yaml)
    export HORREUM_URL="http://your-horreum-instance:8080"
    export HORREUM_API_KEY="HUSR_00000000_0000_0000_0000_000000000000"
    python3 horreum_api_example.py

    # Using custom config file via command line
    python3 horreum_api_example.py --config-file my_config.yaml

    # Using custom config file via environment variable
    export HORREUM_CONFIG_FILE="my_config.yaml"
    python3 horreum_api_example.py

    # Execute changes (disable dry-run mode)
    export DRY_RUN=false
    python3 horreum_api_example.py

    # Disable cleanup operations
    export CLEANUP_LABELS=false
    export CLEANUP_VARIABLES=false
    python3 horreum_api_example.py

    # Using existing resources
    export HORREUM_SCHEMA_ID=285
    export HORREUM_TEST_ID=399
    python3 horreum_api_example.py

    # Force execution without dry run (use with caution)
    export DRY_RUN=false
    python3 horreum_api_example.py
"""

import json
import yaml
import requests
import requests.exceptions
from typing import List, Dict, Any
import sys
import os
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HorreumAPI:
    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        token: str = None,
        api_key: str = None,
        dry_run: bool = False,
    ):
        """Initialize Horreum API client"""
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.dry_run = dry_run
        # Set up authentication - API key takes precedence
        if api_key:
            self.session.headers.update({"X-Horreum-API-Key": api_key})
        elif token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            # For basic auth or token retrieval if needed
            pass
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def create_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new test in Horreum"""
        url = f"{self.base_url}/api/test"
        response = self.session.post(url, json=test_data)
        response.raise_for_status()
        return response.json()

    def update_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing test in Horreum"""
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would update test: {test_data.get('name', 'N/A')} "
                f"(ID: {test_data.get('id', 'N/A')})"
            )
            return test_data

        url = f"{self.base_url}/api/test"
        response = self.session.put(url, json=test_data)
        response.raise_for_status()
        return response.json()

    def create_schema(self, schema_data: Dict[str, Any]) -> int:
        """Create a new schema in Horreum"""
        url = f"{self.base_url}/api/schema"
        logger.info(f"Creating schema at: {url}")
        try:
            response = self.session.post(url, json=schema_data)
            response.raise_for_status()
            return response.json()  # Returns schema ID
        except requests.exceptions.HTTPError as e:
            logger.error(f"Schema creation failed: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            logger.error(f"Schema data keys: {list(schema_data.keys())}")
            logger.error(f"Schema URI: {schema_data.get('uri', 'N/A')}")

            # Re-raise with the response text for easier handling
            raise Exception(f"Schema creation failed: {e.response.text}") from e

    def create_label(
        self, schema_id: int, label_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a label for a schema"""
        if self.dry_run:
            logger.info("[DRY RUN] Would create label:")
            logger.info(f"   Name: {label_data.get('name', 'N/A')}")
            logger.info(
                f"   JSONPath: {label_data.get('extractors', [{}])[0].get('jsonpath', 'N/A')}"
            )
            logger.info(f"   Schema ID: {schema_id}")
            logger.info(f"   URL: POST {self.base_url}/api/schema/{schema_id}/labels")
            # Return a mock response for dry run
            return {
                "id": 777,  # Mock ID
                "name": label_data.get("name", "label-name"),
                "schemaId": schema_id,
            }

        url = f"{self.base_url}/api/schema/{schema_id}/labels"
        response = self.session.post(url, json=label_data)
        response.raise_for_status()
        return response.json()

    def get_schema_labels(self, schema_id: int) -> List[Dict[str, Any]]:
        """Get existing labels for a schema"""
        url = f"{self.base_url}/api/schema/{schema_id}/labels"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def delete_label(self, schema_id: int, label_id: int) -> bool:
        """Delete a label from a schema"""
        if self.dry_run:
            logger.info("[DRY RUN] Would delete label:")
            logger.info(f"   Label ID: {label_id}")
            logger.info(f"   Schema ID: {schema_id}")
            logger.info(
                f"   URL: DELETE {self.base_url}/api/schema/{schema_id}/labels/{label_id}"
            )
            return True

        try:
            url = f"{self.base_url}/api/schema/{schema_id}/labels/{label_id}"
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to delete label {label_id}: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Error deleting label {label_id}: {e}")
            return False

    def get_schema_by_name(self, schema_name: str) -> Dict[str, Any]:
        """Get schema by name"""
        try:
            url = f"{self.base_url}/api/schema"
            response = self.session.get(url)
            response.raise_for_status()
            response_data = response.json()

            # Handle different response formats
            if isinstance(response_data, dict) and "schemas" in response_data:
                # Response is wrapped in {"schemas": [...]}
                schemas = response_data["schemas"]
            elif isinstance(response_data, list):
                # Response is directly a list
                schemas = response_data
            else:
                logger.info(f"Unexpected schema response format: {type(response_data)}")
                keys = (
                    list(response_data.keys())
                    if isinstance(response_data, dict)
                    else "Not a dict"
                )
                logger.info(f"Response keys: {keys}")
                return None

            if not isinstance(schemas, list):
                logger.info(f"Unexpected schema list format: {type(schemas)}")
                return None

            for schema in schemas:
                if isinstance(schema, dict) and schema.get("name") == schema_name:
                    return schema
            return None
        except Exception as e:
            logger.warning(f"Warning: Could not retrieve schemas: {e}")
            return None

    def get_test_by_name(self, test_name: str) -> Dict[str, Any]:
        """Get test by name"""
        try:
            url = f"{self.base_url}/api/test"
            response = self.session.get(url)
            response.raise_for_status()
            response_data = response.json()

            # Handle different response formats (similar to schema handling)
            if isinstance(response_data, dict) and "tests" in response_data:
                # Response is wrapped in {"tests": [...]}
                tests = response_data["tests"]
            elif isinstance(response_data, list):
                # Response is directly a list
                tests = response_data
            else:
                logger.info(f"Unexpected test response format: {type(response_data)}")
                if isinstance(response_data, dict):
                    logger.info(f"Response keys: {list(response_data.keys())}")
                return None

            if not isinstance(tests, list):
                logger.info(f"Unexpected test list format: {type(tests)}")
                return None

            for test in tests:
                if isinstance(test, dict) and test.get("name") == test_name:
                    return test
            return None
        except Exception as e:
            logger.warning(f"Warning: Could not retrieve tests: {e}")
            return None

    def create_change_detection_variable(
        self, test_id: int, variable_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a change detection variable for a test"""
        # Use the correct endpoint and format based on OpenAPI spec
        url = f"{self.base_url}/api/alerting/variables"
        params = {"test": test_id}

        # Convert to the correct format - API expects array of variables
        variables_array = [variable_data]

        logger.info(f"Creating variable at: {url}?test={test_id}")
        logger.info(f"Variable data: {json.dumps(variable_data, indent=2)}")

        try:
            response = self.session.post(url, params=params, json=variables_array)
            response.raise_for_status()
            logger.info("Variable created successfully")

            # Handle the case where response is empty or not JSON
            try:
                if response.text.strip():
                    return response.json()
                else:
                    # Empty response - return success indicator
                    return {
                        "status": "success",
                        "message": "Variable created successfully",
                    }
            except json.JSONDecodeError:
                # Non-JSON response - return success indicator
                return {
                    "status": "success",
                    "message": "Variable created successfully",
                    "response_text": response.text,
                }

        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed with {e.response.status_code}: {e}")
            logger.error(f"Response text: {e.response.text}")
            raise

    def get_test_variables(self, test_id: int) -> List[Dict[str, Any]]:
        """Get existing change detection variables for a test"""
        # Use the correct endpoint and parameter name based on OpenAPI spec
        url = f"{self.base_url}/api/alerting/variables"
        params = {"test": test_id}  # Parameter name is "test", not "testId"
        logger.info(f"Getting variables from: {url}?test={test_id}")

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            variables = response.json()
            logger.info(f"Retrieved {len(variables)} variables")
            return variables
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to get variables: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")
            # Return empty list but don't crash - this is not critical
            logger.warning("Could not get variables, returning empty list")
            return []

    def update_variables(self, test_id: int, variables: List[Dict[str, Any]]) -> bool:
        """Update variables (upsert) for a test via /api/alerting/variables.

        The API expects the FULL list of variables for the given test. Any variables
        omitted from the list may be removed on the server. Always send all current
        variables with any desired modifications.
        """
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would update {len(variables)} variables for test {test_id}"
            )
            return True

        url = f"{self.base_url}/api/alerting/variables"
        params = {"test": test_id}

        logger.info(f"Updating variables at: {url}?test={test_id}")
        logger.info(f"Sending {len(variables)} variables to server")

        # Debug: Show a summary of what we're sending
        for i, var in enumerate(variables):
            var_name = var.get("name", "unnamed")
            has_cd = bool(var.get("changeDetection"))
            cd_count = len(var.get("changeDetection", []))
            logger.info(
                f"  [{i+1}] {var_name} (changeDetection: {has_cd}, entries: {cd_count})"
            )

        try:
            response = self.session.post(url, params=params, json=variables)
            logger.info(f"Server response: {response.status_code}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"Update successful. Response: {result}")
                except (ValueError, json.JSONDecodeError):
                    logger.info("Update successful (no JSON response)")
                return True
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update variables: {e}")
            if hasattr(e, "response") and e.response:
                logger.error(f"   Status code: {e.response.status_code}")
                logger.error(f"   Response text: {e.response.text[:500]}")
            return False
        except Exception as e:
            logger.error(f"Failed to update variables: {e}")
            return False

        return True

    def delete_variable(self, variable_id: int) -> bool:
        """Delete a change detection variable"""
        if self.dry_run:
            logger.info("[DRY RUN] Would delete variable:")
            logger.info(f"   Variable ID: {variable_id}")
            logger.info(
                f"   URL: DELETE {self.base_url}/api/alerting/variables/{variable_id}"
            )
            return True

        try:
            url = f"{self.base_url}/api/alerting/variables/{variable_id}"
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Failed to delete variable {variable_id}: {e.response.status_code}"
            )
            logger.error(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Error deleting variable {variable_id}: {e}")
            return False

    def create_multiple_change_detection_variables(self, test_id, variables_data):
        """Update/replace ALL change detection variables for a test in a single API call.

        IMPORTANT: This API endpoint replaces ALL existing variables with the provided list.
        To preserve existing variables, you must include them in variables_data.
        """
        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would update/replace ALL variables with {len(variables_data)} total variables:"
            )
            for i, var in enumerate(variables_data[:10]):  # Show first 10
                logger.info(
                    f"   {i+1}. {var.get('name', 'N/A')} (group: {var.get('group', 'N/A')})"
                )
            if len(variables_data) > 10:
                logger.info(f"   ... and {len(variables_data) - 10} more")
            logger.info(f"   Test ID: {test_id}")
            logger.info(
                f"   URL: POST {self.base_url}/api/alerting/variables?test={test_id}"
            )
            return {"status": "success", "message": "Variables would be updated"}

        url = f"{self.base_url}/api/alerting/variables"
        params = {"test": test_id}

        logger.info(
            f"Updating/replacing ALL variables with {len(variables_data)} total variables at: {url}"
        )
        # Note: Detailed variable data output removed to avoid excessive logging

        response = self.session.post(url, json=variables_data, params=params)

        if response.status_code in [200, 201, 204]:  # All success codes
            logger.info(
                f"Variables updated successfully (status: {response.status_code})"
            )
            try:
                return (
                    response.json()
                    if response.text
                    else {"status": "success", "message": "Variables updated"}
                )
            except (ValueError, json.JSONDecodeError):
                return {"status": "success", "message": "Variables updated"}
        else:
            logger.error(f"Failed to update variables: {response.status_code}")
            logger.info(f"Response: {response.text}")
            response.raise_for_status()


def load_field_config(
    config_file: str = "horreum_fields_config.yaml",
) -> Dict[str, Any]:
    """Load field configuration from YAML file"""

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config


def process_field_definitions(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process field definitions from configuration"""

    field_definitions = []

    for field in config.get("fields", []):
        # Add "__" prefix to all field names
        label_name = f"__{field['name']}"

        field_definitions.append(
            {
                "label_name": label_name,
                "jsonpath": field["jsonpath"],
                "description": field.get("description", ""),
                "filtering": field.get("filtering", False),
                "metrics": field.get("metrics", False),
                "change_detection_group": field.get("change_detection_group"),
            }
        )

    return field_definitions


def create_json_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a JSON schema based on the field configuration"""

    # Build schema properties from field definitions
    properties = {
        "name": {"type": "string", "description": "Test name"},
        "ended": {"type": "string", "description": "Test end timestamp"},
        "$schema": {"type": "string", "description": "Schema identifier"},
        "jobLink": {
            "type": "string",
            "description": "Link to the job that generated this data",
        },
        "started": {"type": "string", "description": "Test start timestamp"},
    }

    # Parse field JSONPaths to build nested schema structure
    def add_path_to_schema(
        properties: Dict[str, Any], path_parts: List[str], field_info: Dict[str, Any]
    ):
        """Recursively add a JSONPath to the schema properties"""
        if not path_parts:
            return

        current_part = path_parts[0]
        remaining_parts = path_parts[1:]

        # Handle quoted keys (like "tekton-pipelines-controller")
        if current_part.startswith('"') and current_part.endswith('"'):
            current_part = current_part[1:-1]

        if not remaining_parts:
            # Leaf node - determine type based on field name
            field_type = "number"
            keywords = ["id", "name", "started", "ended", "link"]
            if any(
                keyword in field_info.get("name", "").lower() for keyword in keywords
            ):
                field_type = "string"

            properties[current_part] = {
                "type": field_type,
                "description": field_info.get(
                    "description", f"Value for {current_part}"
                ),
            }
        else:
            # Intermediate node - create object if it doesn't exist
            if current_part not in properties:
                properties[current_part] = {
                    "type": "object",
                    "properties": {},
                    "description": f"Container for {current_part} related metrics",
                }
            elif properties[current_part].get("type") != "object":
                # Convert to object if it wasn't already
                properties[current_part] = {
                    "type": "object",
                    "properties": {},
                    "description": f"Container for {current_part} related metrics",
                }

            # Recursively add remaining path
            add_path_to_schema(
                properties[current_part]["properties"], remaining_parts, field_info
            )

    # Process all fields from configuration
    for field in config.get("fields", []):
        jsonpath = field.get("jsonpath", "")
        if jsonpath.startswith("$."):
            # Remove $. prefix and split path
            path = jsonpath[2:]
            path_parts = []

            # Split path while preserving quoted segments
            current_part = ""
            in_quotes = False

            for char in path:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == "." and not in_quotes:
                    if current_part:
                        path_parts.append(current_part)
                        current_part = ""
                else:
                    current_part += char

            if current_part:
                path_parts.append(current_part)

            add_path_to_schema(properties, path_parts, field)

    # Get JSON schema metadata from configuration
    schema_config = config.get("schema", {})
    json_schema_config = schema_config.get("json_schema", {})

    # Create the complete JSON schema using configuration values
    schema = {
        "$schema": json_schema_config.get(
            "$schema", "https://json-schema.org/draft/2020-12/schema"
        ),
        "$id": json_schema_config.get(
            "$id", schema_config["uri"]
        ),  # uri is now mandatory
        "title": json_schema_config.get("title", "Performance Test Schema"),
        "description": json_schema_config.get(
            "description", "Schema for performance benchmark data"
        ),
        "type": "object",
        "properties": properties,
        "required": ["name", "$schema"],
    }

    return schema


def create_fingerprint_labels(fields: List[Dict[str, Any]]) -> List[str]:
    """Create fingerprint labels from fields that have filtering=true and no change detection"""
    fingerprint_labels = []

    for field in fields:
        # Check if field has filtering set to true
        if not field.get("filtering", False):
            continue

        # Check if field has no change detection group or it's set to null
        change_detection_group = field.get("change_detection_group")
        if change_detection_group is not None:
            continue

        # Add the field name to fingerprint labels (using label_name if available, otherwise name)
        label_name = field.get("label_name") or field.get("name")
        if label_name:
            fingerprint_labels.append(label_name)
            logger.info(
                f"Added '{label_name}' to fingerprint labels (filtering=true, no change detection)"
            )

    logger.info(
        f"Generated {len(fingerprint_labels)} fingerprint labels: {fingerprint_labels}"
    )
    return fingerprint_labels


def create_test_definition(
    config: Dict[str, Any], fields: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create the test definition from configuration with dynamic fingerprint labels"""
    test_config = config.get("test", {})
    if not test_config:
        raise ValueError("No 'test' configuration found in horreum_fields_config.yaml")

    # Validate mandatory fields
    if "owner" not in test_config:
        raise ValueError(
            "Mandatory field 'owner' is missing from 'test' section in horreum_fields_config.yaml"
        )
    if "name" not in test_config:
        raise ValueError(
            "Mandatory field 'name' is missing from 'test' section in horreum_fields_config.yaml"
        )
    if "folder" not in test_config:
        raise ValueError(
            "Mandatory field 'folder' is missing from 'test' section in horreum_fields_config.yaml"
        )

    # Create a copy of test config
    test_def = dict(test_config)

    # Generate dynamic fingerprint labels
    fingerprint_labels = create_fingerprint_labels(fields)
    if fingerprint_labels:
        logger.info(
            f"Setting fingerprintLabels in test definition: {fingerprint_labels}"
        )
        test_def["fingerprintLabels"] = fingerprint_labels
    else:
        logger.info(
            "No fields qualify for fingerprint labels, using static configuration"
        )

    return test_def


def create_schema_definition(
    config: Dict[str, Any], json_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """Create the schema definition from configuration"""
    schema_config = config.get("schema", {})
    if not schema_config:
        raise ValueError(
            "No 'schema' configuration found in horreum_fields_config.yaml"
        )

    # Validate mandatory fields
    if "owner" not in schema_config:
        raise ValueError(
            "Mandatory field 'owner' is missing from 'schema' section in horreum_fields_config.yaml"
        )
    if "uri" not in schema_config:
        raise ValueError(
            "Mandatory field 'uri' is missing from 'schema' section in horreum_fields_config.yaml"
        )
    if "name" not in schema_config:
        raise ValueError(
            "Mandatory field 'name' is missing from 'schema' section in horreum_fields_config.yaml"
        )

    # Create schema definition from config
    schema_def = dict(schema_config)  # Convert to regular dict
    schema_def["schema"] = json.dumps(json_schema)  # Add the generated JSON schema

    return schema_def


def create_label_definitions(
    fields: List[Dict[str, Any]], schema_id: int, config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Create label definitions for all extracted fields"""
    labels = []

    # Get global configuration values
    global_config = config.get("global", {})
    if "owner" not in global_config:
        raise ValueError(
            "Mandatory field 'owner' is missing from 'global' section in horreum_fields_config.yaml"
        )
    default_owner = global_config["owner"]
    default_access = global_config.get("access", "PUBLIC")

    for field in fields:
        label = {
            "access": default_access,
            "owner": default_owner,
            "name": field["label_name"],
            "extractors": [
                {"name": "value", "jsonpath": field["jsonpath"], "isarray": False}
            ],
            "function": "value => value",
            "filtering": field["filtering"],
            "metrics": field["metrics"],
            "schemaId": schema_id,
        }

        labels.append(label)

    return labels


def group_labels_for_change_detection(
    fields: List[Dict[str, Any]],
) -> Dict[str, List[str]]:
    """Group labels by logical categories for change detection using configuration"""
    groups = {}

    for field in fields:
        change_detection_group = field.get("change_detection_group")
        if change_detection_group:  # Only include fields with change detection enabled
            if change_detection_group not in groups:
                groups[change_detection_group] = []
            groups[change_detection_group].append(field["label_name"])

    return groups


def create_change_detection_variables(
    test_id: int, fields: List[Dict[str, Any]], config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Create change detection variable definitions - one per label using configuration"""
    variables = []

    # Get change detection configuration
    change_detection_groups = config.get("change_detection_groups", {})
    defaults = config.get("change_detection_defaults", {})

    # Create one variable per field that has change detection enabled
    for field in fields:
        change_detection_group = field.get("change_detection_group")
        if not change_detection_group:
            continue  # Skip fields without change detection

        label_name = field["label_name"]

        # Get group-specific configuration or use defaults
        group_config = change_detection_groups.get(change_detection_group, {})

        # Determine the model type
        model = group_config.get("model", defaults.get("model", "relativeDifference"))

        # Create configuration based on model type
        if model == "fixedThreshold":
            # Fixed Threshold configuration
            group_ft_config = group_config.get("fixed_threshold", {})
            defaults_ft_config = defaults.get("fixed_threshold", {})

            change_detection_config = {
                "model": "fixedThreshold",
                "config": {
                    "include": [label_name],  # Label filter
                    "exclude": [],
                    "min": {
                        "enabled": group_ft_config.get(
                            "min_enabled", defaults_ft_config.get("min_enabled", False)
                        ),
                        "value": group_ft_config.get(
                            "min_value", defaults_ft_config.get("min_value")
                        ),
                        "inclusive": group_ft_config.get(
                            "min_inclusive",
                            defaults_ft_config.get("min_inclusive", True),
                        ),
                    },
                    "max": {
                        "enabled": group_ft_config.get(
                            "max_enabled", defaults_ft_config.get("max_enabled", False)
                        ),
                        "value": group_ft_config.get(
                            "max_value", defaults_ft_config.get("max_value")
                        ),
                        "inclusive": group_ft_config.get(
                            "max_inclusive",
                            defaults_ft_config.get("max_inclusive", True),
                        ),
                    },
                },
            }
        elif model == "eDivisive":
            # eDivisive-Hunter configuration (simple - no complex parameters needed)
            change_detection_config = {
                "model": "eDivisive",
                "config": {
                    "include": [label_name],  # Label filter
                    "exclude": [],
                    # eDivisive uses Hunter tool with fixed configuration - no user parameters needed
                },
            }
        else:
            # Relative Difference configuration (default)
            change_detection_config = {
                "model": "relativeDifference",
                "config": {
                    # Aggregation function
                    "filter": group_config.get(
                        "aggregation", defaults.get("aggregation", "mean")
                    ),
                    "include": [label_name],  # Single label per variable (label filter)
                    "exclude": [],
                    "window": group_config.get("window", defaults.get("window", 10)),
                    "minPrevious": group_config.get(
                        "min_previous", defaults.get("min_previous", 5)
                    ),
                    "threshold": group_config.get(
                        "threshold", defaults.get("threshold", 0.1)
                    ),
                },
            }

        variable = {
            "name": label_name,  # Use label name as variable name
            "group": change_detection_group,
            "testId": test_id,
            "order": len(variables) + 1,  # Add order field as required by schema
            "labels": [label_name],  # Single label array
            "calculation": "mean",
            "changeDetection": [
                change_detection_config
            ],  # Array format per OpenAPI spec
            "description": group_config.get(
                "description", f"Change detection for {label_name} metric"
            ),
        }

        variables.append(variable)

    return variables


def _resolve_group_config(config: Dict[str, Any], group_name: str) -> Dict[str, Any]:
    """Resolve desired change detection configuration for a group using defaults.

    Returns dict with keys based on model type:
    - relativeDifference: model, window, minPrevious, threshold, aggregation
    - fixedThreshold: model, min_enabled, min_value, min_inclusive, max_enabled, max_value, max_inclusive
    - eDivisive: model (no additional parameters - uses Hunter algorithm)
    """
    groups = config.get("change_detection_groups", {})
    defaults = config.get("change_detection_defaults", {})
    group_cfg = groups.get(group_name, {}) if group_name else {}

    model = group_cfg.get("model", defaults.get("model", "relativeDifference"))

    if model == "fixedThreshold":
        # Fixed Threshold configuration
        group_ft_config = group_cfg.get("fixed_threshold", {})
        defaults_ft_config = defaults.get("fixed_threshold", {})

        desired = {
            "model": model,
            "min_enabled": group_ft_config.get(
                "min_enabled", defaults_ft_config.get("min_enabled", False)
            ),
            "min_value": group_ft_config.get(
                "min_value", defaults_ft_config.get("min_value")
            ),
            "min_inclusive": group_ft_config.get(
                "min_inclusive", defaults_ft_config.get("min_inclusive", True)
            ),
            "max_enabled": group_ft_config.get(
                "max_enabled", defaults_ft_config.get("max_enabled", False)
            ),
            "max_value": group_ft_config.get(
                "max_value", defaults_ft_config.get("max_value")
            ),
            "max_inclusive": group_ft_config.get(
                "max_inclusive", defaults_ft_config.get("max_inclusive", True)
            ),
        }
    elif model == "eDivisive":
        # eDivisive-Hunter configuration (simple - no user parameters)
        desired = {
            "model": model,
            # eDivisive doesn't have configurable parameters - uses fixed Hunter configuration
        }
    else:
        # Relative Difference configuration (default)
        desired = {
            "model": model,
            "window": group_cfg.get("window", defaults.get("window")),
            "minPrevious": group_cfg.get("min_previous", defaults.get("min_previous")),
            "threshold": group_cfg.get("threshold", defaults.get("threshold")),
            "aggregation": group_cfg.get(
                "aggregation", defaults.get("aggregation", "mean")
            ),
        }

    return desired


def _extract_change_detection_values(
    cd_config: Dict[str, Any], model: str
) -> Dict[str, Any]:
    """Extract comparable values from a server-side change detection config object."""
    if not isinstance(cd_config, dict):
        return {}

    if model == "fixedThreshold":
        # Extract fixed threshold values
        min_config = cd_config.get("min", {})
        max_config = cd_config.get("max", {})

        return {
            "model": model,
            "min_enabled": min_config.get("enabled", False),
            "min_value": min_config.get("value"),
            "min_inclusive": min_config.get("inclusive", True),
            "max_enabled": max_config.get("enabled", False),
            "max_value": max_config.get("value"),
            "max_inclusive": max_config.get("inclusive", True),
        }
    elif model == "eDivisive":
        # Extract eDivisive values (simple - no configuration parameters)
        return {
            "model": model,
            # eDivisive doesn't have configurable parameters - just the model type
        }
    else:
        # Extract relative difference values (default)
        return {
            "model": model,
            "window": cd_config.get("window"),
            "minPrevious": cd_config.get("minPrevious"),
            "threshold": cd_config.get("threshold"),
            "aggregation": cd_config.get(
                "filter", "mean"
            ),  # Server stores aggregation as 'filter'
        }


def _needs_update(existing: Dict[str, Any], desired: Dict[str, Any]) -> bool:
    """Whether existing change detection values differ from desired ones."""
    if not existing:
        return True

    # Check model type first
    model = desired.get("model", "relativeDifference")
    if existing.get("model") != model:
        return True

    if model == "fixedThreshold":
        # Compare fixed threshold values
        for key in (
            "min_enabled",
            "min_value",
            "min_inclusive",
            "max_enabled",
            "max_value",
            "max_inclusive",
        ):
            if existing.get(key) != desired.get(key):
                return True
    elif model == "eDivisive":
        # eDivisive has no configurable parameters - only check model type
        # If we reach here and models match, no update needed
        pass
    else:
        # Compare relative difference values
        for key in ("window", "minPrevious", "threshold", "aggregation"):
            if existing.get(key) != desired.get(key):
                return True

    return False


def sync_change_detection_configs(
    api: HorreumAPI, test_id: int, fields: List[Dict[str, Any]], config: Dict[str, Any]
) -> None:
    """Ensure server variables match YAML change detection config.

    - Fetch all variables for test
    - For each field with a change_detection_group, compare and update the variable's
      changeDetection config on the server when different.
    - Supports all three models:
      - relativeDifference: threshold, window, minPrevious, aggregation
      - fixedThreshold: min/max enabled, value, inclusive settings
      - eDivisive: Hunter algorithm with automatic change point detection (no parameters)
    """
    import copy

    logger.info("\nSynchronizing change detection configs with server...")
    server_variables = api.get_test_variables(test_id)

    if not server_variables:
        logger.info("No variables found on server. Nothing to synchronize.")
        return

    logger.info(f"Found {len(server_variables)} variables on server")

    # Make a deep copy to avoid modifying original data
    variables_to_update = copy.deepcopy(server_variables)

    # Map variable name -> variable object from server (using the copy)
    # Create mapping of variable name to variable object
    vars_by_name: Dict[str, Dict[str, Any]] = {
        v.get("name"): v
        for v in variables_to_update
        if isinstance(v, dict) and v.get("name")
    }

    logger.info(f"Variables by name: {list(vars_by_name.keys())}")

    # Track updates
    updated_names: List[str] = []
    update_details: List[str] = []
    no_update_needed: List[str] = []

    for field in fields:
        group = field.get("change_detection_group")
        if not group:
            continue

        var_name = field.get("label_name")
        if not var_name:
            logger.info(f"Field missing label_name: {field}")
            continue

        if var_name not in vars_by_name:
            logger.info(f"Variable '{var_name}' not found on server")
            continue

        desired = _resolve_group_config(config, group)
        variable = vars_by_name[var_name]
        cd_list = variable.get("changeDetection", [])

        # Choose the first change detection entry to update (or create a new one)
        if cd_list and isinstance(cd_list, list) and len(cd_list) > 0:
            cd_entry = cd_list[0]
        else:
            cd_entry = {
                "id": -1,  # new entry marker; backend will create
                "model": desired.get("model", "relativeDifference"),
                "config": {},
            }
            cd_list = [cd_entry]
            variable["changeDetection"] = cd_list
            # Only log when creating new entries
            logger.info(f"Created new CD entry for {var_name}: {cd_entry}")

        # Determine model type from existing or desired configuration
        current_model = cd_entry.get("model", "relativeDifference")
        desired_model = desired.get("model", "relativeDifference")

        existing_values = _extract_change_detection_values(
            cd_entry.get("config", {}), current_model
        )

        if _needs_update(existing_values, desired):
            # Only show verbose logging for variables that need updates
            logger.info(
                f"Processing variable '{var_name}' with group '{group}': desired={desired}"
            )
            logger.info(f"   Current changeDetection: {cd_list}")
            logger.info(f"   Using existing CD entry: {cd_entry}")
            logger.info(f"   Existing values: {existing_values}")
            logger.info(f"   Desired values: {desired}")
            # Update configuration based on model type
            old_config = cd_entry.get("config", {})
            new_cfg = dict(old_config)

            if desired_model == "fixedThreshold":
                # Update fixed threshold configuration
                new_cfg["min"] = {
                    "enabled": desired["min_enabled"],
                    "value": desired["min_value"],
                    "inclusive": desired["min_inclusive"],
                }
                new_cfg["max"] = {
                    "enabled": desired["max_enabled"],
                    "value": desired["max_value"],
                    "inclusive": desired["max_inclusive"],
                }
            elif desired_model == "eDivisive":
                # eDivisive configuration - no parameters needed, just ensure include/exclude are preserved
                # The existing include/exclude labels should be maintained
                pass
            else:
                # Update relative difference configuration
                new_cfg["window"] = desired["window"]
                new_cfg["minPrevious"] = desired["minPrevious"]
                new_cfg["threshold"] = desired["threshold"]
                new_cfg["filter"] = desired[
                    "aggregation"
                ]  # Set aggregation function as 'filter'

            cd_entry["config"] = new_cfg
            cd_entry["model"] = desired_model

            updated_names.append(var_name)
            update_details.append(
                f"   {var_name} ({desired_model}): {old_config} → {new_cfg}"
            )
            logger.info(f"   Marked for update: {var_name}")
        else:
            # Just track variables that don't need updates, don't log each one
            no_update_needed.append(var_name)

    if updated_names:
        logger.info(f"\nFound {len(updated_names)} variable(s) to update:")
        for name in updated_names:
            logger.info(f"  - {name}")

        logger.info("\nUpdate details:")
        for detail in update_details:
            logger.info(detail)

        # Debug: Show what we're sending to server
        logger.info(f"\nSending {len(variables_to_update)} variables to server...")
        if api.dry_run:
            logger.info("[DRY RUN] Variable data that would be sent:")
            for var in variables_to_update:
                if var.get("name") in updated_names:
                    logger.info(f"  Variable: {var.get('name')}")
                    logger.info(f"    changeDetection: {var.get('changeDetection')}")

        # IMPORTANT: Send full list back, not just updated ones
        result = api.update_variables(test_id, variables_to_update)
        if result:
            logger.info("Server change detection configs synchronized.")
        else:
            logger.error("Failed to synchronize server change detection configs.")
    else:
        if no_update_needed:
            logger.info(
                f"All {len(no_update_needed)} variables are up to date. No synchronization needed."
            )
        else:
            logger.info("No differences found. Server is up to date.")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Horreum API Integration Script for Performance Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  HORREUM_URL              - Horreum instance URL (required)
  HORREUM_API_KEY          - API key for authentication (required)
  HORREUM_CONFIG_FILE      - Path to configuration file (default: horreum_fields_config.yaml)
  HORREUM_SCHEMA_ID        - Use existing schema ID (optional)
  HORREUM_TEST_ID          - Use existing test ID (optional)
  SKIP_LABELS              - Skip label creation (default: false)
  CLEANUP_LABELS           - Enable removal of obsolete labels (default: true)
  CLEANUP_VARIABLES        - Enable removal of obsolete variables (default: true)
  DRY_RUN                  - Dry run mode (default: true)

Examples:
  python3 horreum_api_example.py
  python3 horreum_api_example.py --config-file my_config.yaml
  python3 horreum_api_example.py -c custom_fields.yaml
        """,
    )

    parser.add_argument(
        "--config-file",
        "-c",
        type=str,
        help="Path to YAML configuration file (overrides HORREUM_CONFIG_FILE environment variable)",
    )

    return parser.parse_args()


def main():
    """Main function to create test and schema in Horreum"""

    # Parse command line arguments
    args = parse_arguments()

    # Configuration - these should be set as environment variables or command line args
    horreum_url = os.getenv("HORREUM_URL")
    horreum_api_key = os.getenv("HORREUM_API_KEY")
    horreum_token = os.getenv("HORREUM_TOKEN")  # Keep for backward compatibility
    existing_schema_id = os.getenv("HORREUM_SCHEMA_ID")  # Optional existing schema ID
    existing_test_id = os.getenv("HORREUM_TEST_ID")  # Optional existing test ID
    skip_labels = (
        os.getenv("SKIP_LABELS", "false").lower() == "true"
    )  # Skip label creation
    dry_run = (
        os.getenv("DRY_RUN", "true").lower() == "true"
    )  # Dry run mode (default: enabled)

    # Determine config file to use (command line arg takes precedence)
    config_file = (
        args.config_file
        or os.getenv("HORREUM_CONFIG_FILE")
        or "horreum_fields_config.yaml"
    )

    if dry_run:
        logger.info("DRY RUN MODE ENABLED - No changes will be made")
        logger.info("=" * 50)

    # Log the config file being used
    logger.info(f"Using configuration file: {config_file}")

    if not horreum_api_key and not horreum_token:
        logger.error(
            "Error: HORREUM_API_KEY or HORREUM_TOKEN environment variable is required"
        )
        logger.info(
            "Preferred: export HORREUM_API_KEY='HUSR_00000000_0000_0000_0000_000000000000'"
        )
        sys.exit(1)

    try:
        # Initialize API client - prefer API key over token
        if horreum_api_key:
            api = HorreumAPI(horreum_url, api_key=horreum_api_key, dry_run=dry_run)
        else:
            api = HorreumAPI(horreum_url, token=horreum_token, dry_run=dry_run)

        # Load field configuration
        logger.info("Loading field configuration...")
        config = load_field_config(config_file)

        # Process field definitions
        logger.info("Processing field definitions...")
        fields = process_field_definitions(config)
        logger.info(f"Found {len(fields)} fields")

        # Initialize tracking variables
        removed_labels = []
        removed_variables = []
        schema_created = False
        test_created = False

        # Create JSON schema
        logger.info("Creating JSON schema...")
        json_schema = create_json_schema(config)

        # Create or use existing schema
        if existing_schema_id:
            schema_id = int(existing_schema_id)
            schema_created = False
            logger.info(f"Using existing schema ID from environment: {schema_id}")
        else:
            schema_def = create_schema_definition(config, json_schema)

            # First check if schema already exists (even in dry-run mode)
            logger.info("Checking for existing schema...")
            existing_schema = api.get_schema_by_name(schema_def["name"])

            if existing_schema:
                schema_id = existing_schema["id"]
                schema_created = False
                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would use existing schema: {schema_def['name']} (ID: {schema_id})"
                    )
                else:
                    logger.info(
                        f"Found existing schema: {schema_def['name']} (ID: {schema_id})"
                    )
            else:
                # Schema doesn't exist, need to create it
                schema_created = True
                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would create new schema: {schema_def['name']}"
                    )
                    schema_id = 888  # Mock ID for dry-run
                else:
                    logger.info("Creating schema in Horreum...")
                    try:
                        schema_id = api.create_schema(schema_def)
                        logger.info(f"Created schema with ID: {schema_id}")
                    except Exception as e:
                        if "Name already used" in str(e) or "already exists" in str(e):
                            logger.info(
                                f"Schema '{schema_def['name']}' already exists (race condition)"
                            )
                            logger.info("Looking up existing schema...")
                            existing_schema = api.get_schema_by_name(schema_def["name"])
                            if existing_schema:
                                schema_id = existing_schema["id"]
                                logger.info(
                                    f"Found existing schema: {schema_def['name']} (ID: {schema_id})"
                                )
                            else:
                                logger.warning("Could not find existing schema by name")
                                logger.error(
                                    "This is unexpected since the creation failed due to name conflict."
                                )
                                logger.info(
                                    "Please check your permissions or set "
                                    "HORREUM_SCHEMA_ID environment variable."
                                )
                                sys.exit(1)
                        else:
                            raise

        # Create or use existing test
        if existing_test_id:
            test_name = config["test"]["name"]  # name is now mandatory
            test_id = int(existing_test_id)
            test_created = False
            logger.info(f"Using existing test ID from environment: {existing_test_id}")

            # Get full test details and check fingerprint labels
            try:
                existing_test = api.get_test_by_name(test_name)
                if existing_test and existing_test["id"] == test_id:
                    test_def = create_test_definition(config, fields)

                    # Check if fingerprint labels need to be updated
                    existing_fingerprint_labels = existing_test.get(
                        "fingerprintLabels", []
                    )
                    new_fingerprint_labels = test_def.get("fingerprintLabels", [])

                    if existing_fingerprint_labels != new_fingerprint_labels:
                        logger.info("Updating test fingerprint labels:")
                        logger.info(f"  Current: {existing_fingerprint_labels}")
                        logger.info(f"  New: {new_fingerprint_labels}")

                        # Create updated test data with new fingerprint labels
                        updated_test_data = dict(existing_test)
                        updated_test_data["fingerprintLabels"] = new_fingerprint_labels

                        # Update the test
                        test = api.update_test(updated_test_data)
                        if not dry_run:
                            logger.info("Updated test fingerprint labels successfully")
                    else:
                        test = existing_test
                        logger.info(
                            f"Test fingerprint labels are up to date: {existing_fingerprint_labels}"
                        )
                else:
                    # Fallback to basic test object if name lookup fails
                    test = {"id": test_id, "name": test_name}
                    logger.warning(
                        "Could not retrieve full test details for fingerprint label check"
                    )
            except Exception as e:
                # Fallback to basic test object on error
                test = {"id": test_id, "name": test_name}
                logger.warning(f"Error retrieving test details: {e}")
        else:
            test_def = create_test_definition(config, fields)

            # First check if test already exists (even in dry-run mode)
            logger.info("Checking for existing test...")
            existing_test = api.get_test_by_name(test_def["name"])

            if existing_test:
                test = existing_test
                test_created = False
                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would use existing test: {test_def['name']} (ID: {test['id']})"
                    )
                else:
                    logger.info(
                        f"Found existing test: {test_def['name']} (ID: {test['id']})"
                    )

                # Check if fingerprint labels need to be updated
                existing_fingerprint_labels = existing_test.get("fingerprintLabels", [])
                new_fingerprint_labels = test_def.get("fingerprintLabels", [])

                if existing_fingerprint_labels != new_fingerprint_labels:
                    logger.info("Updating test fingerprint labels:")
                    logger.info(f"  Current: {existing_fingerprint_labels}")
                    logger.info(f"  New: {new_fingerprint_labels}")

                    # Create updated test data with new fingerprint labels
                    updated_test_data = dict(existing_test)
                    updated_test_data["fingerprintLabels"] = new_fingerprint_labels

                    # Update the test
                    test = api.update_test(updated_test_data)
                    if not dry_run:
                        logger.info("Updated test fingerprint labels successfully")
                else:
                    logger.info(
                        f"Test fingerprint labels are up to date: {existing_fingerprint_labels}"
                    )
            else:
                # Test doesn't exist, need to create it
                test_created = True
                if dry_run:
                    logger.info(f"[DRY RUN] Would create new test: {test_def['name']}")
                    test = {
                        "id": 999,
                        "name": test_def["name"],
                    }  # Mock data for dry-run
                else:
                    logger.info("Creating test in Horreum...")
                    try:
                        test = api.create_test(test_def)
                        logger.info(f"Created test: {test['name']} (ID: {test['id']})")
                    except Exception as e:
                        if (
                            "409" in str(e)
                            or "Conflict" in str(e)
                            or "already exists" in str(e)
                        ):
                            logger.info(
                                f"Test '{test_def['name']}' already exists (race condition)"
                            )
                            logger.info("Looking up existing test...")
                            existing_test = api.get_test_by_name(test_def["name"])
                            if existing_test:
                                test = existing_test
                                logger.info(
                                    f"Found existing test: {test_def['name']} (ID: {test['id']})"
                                )
                            else:
                                logger.warning("Could not find existing test by name")
                                logger.info(
                                    "Tip: Set HORREUM_TEST_ID environment variable to use existing test"
                                )
                                if dry_run:
                                    logger.info("[DRY RUN] Would prompt for test ID")
                                    test = {"id": 999, "name": test_def["name"]}
                                else:
                                    test_id = int(
                                        input(
                                            "Please enter the existing test ID: "
                                        ).strip()
                                    )
                                    test = {"id": test_id, "name": test_def["name"]}
                                    logger.info(f"Using existing test ID: {test_id}")
                        else:
                            raise

        # Get existing labels to check for duplicates
        if schema_id and not skip_labels:
            logger.info("Checking for existing labels...")
            try:
                existing_labels = api.get_schema_labels(schema_id)
                existing_label_names = {label.get("name") for label in existing_labels}
                logger.info(f"Found {len(existing_labels)} existing labels in schema")
            except Exception as e:
                logger.warning(
                    f"Warning: Could not retrieve existing labels, will attempt to create all: {e}"
                )
                existing_label_names = set()
        else:
            if skip_labels:
                logger.warning("Skipping label operations (SKIP_LABELS=true)")
            else:
                logger.warning("Skipping label operations - no valid schema ID")
            existing_label_names = set()
            created_labels = []
            skipped_labels = []
            failed_labels = []

        # Create labels
        if schema_id and not skip_labels:
            logger.info("Creating labels...")
            label_defs = create_label_definitions(fields, schema_id, config)

            if "created_labels" not in locals():
                created_labels = []
                skipped_labels = []
                failed_labels = []

            for i, label_def in enumerate(label_defs):
                label_name = label_def["name"]

                # Check if label already exists
                if label_name in existing_label_names:
                    skipped_labels.append(label_name)
                    logger.warning(
                        f"Skipped {i+1}/{len(label_defs)}: {label_name} (already exists)"
                    )
                    continue

                # Try to create the label
                try:
                    label = api.create_label(schema_id, label_def)
                    created_labels.append(label)
                    logger.info(f"Created {i+1}/{len(label_defs)}: {label_name}")
                except Exception as e:
                    failed_labels.append((label_name, str(e)))
                    logger.error(f"Failed {i+1}/{len(label_defs)}: {label_name} - {e}")
        else:
            if not skip_labels:
                logger.warning("Skipping label creation - no valid schema ID")
            label_defs = []

        # Cleanup labels that are no longer in configuration
        cleanup_labels = (
            os.getenv("CLEANUP_LABELS", "true").lower() == "true"
        )  # Default: cleanup enabled

        if schema_id and not skip_labels and cleanup_labels:
            logger.info("\nCleaning up obsolete labels...")
            try:
                # Get current labels and compare with configuration
                current_labels = api.get_schema_labels(schema_id)
                current_label_names = {label.get("name") for label in current_labels}

                # Get expected labels from configuration
                expected_label_names = {field["label_name"] for field in fields}

                # Find labels to remove (exist in Horreum but not in config)
                labels_to_remove = current_label_names - expected_label_names

                if labels_to_remove:
                    action = "Would remove" if dry_run else "Found"
                    logger.info(
                        f"{action} {len(labels_to_remove)} obsolete labels {'to remove' if dry_run else ''}:"
                    )
                    for label_name in labels_to_remove:
                        logger.info(f"  - {label_name}")

                    if dry_run:
                        # In dry-run mode, just count what would be removed
                        removed_labels.extend(labels_to_remove)
                        logger.info(
                            f"[DRY RUN] Would remove {len(labels_to_remove)} obsolete labels"
                        )
                    else:
                        # Actually remove obsolete labels
                        for label in current_labels:
                            label_name = label.get("name")
                            label_id = label.get("id")

                            if label_name in labels_to_remove:
                                if api.delete_label(schema_id, label_id):
                                    removed_labels.append(label_name)
                                    logger.info(f"Removed label: {label_name}")
                                else:
                                    logger.error(
                                        f"Failed to remove label: {label_name}"
                                    )
                else:
                    action = "Would find" if dry_run else ""
                    logger.info(f"{action} No obsolete labels found")

            except Exception as e:
                logger.error(f"Label cleanup failed: {e}")
        elif cleanup_labels:
            logger.warning(
                "Skipping label cleanup - no valid schema ID or labels disabled"
            )

        logger.info("\nSummary:")
        if dry_run:
            logger.info("DRY RUN SUMMARY - No actual changes were made:")

        # Schema summary
        if schema_created:
            action = "Would create" if dry_run else "Created"
            schema_name = schema_def["name"] if "schema_de" in locals() else "N/A"
            logger.info(f"- {action} schema: {schema_name} (ID: {schema_id})")
        else:
            action = "Would use" if dry_run else "Using"
            schema_name = schema_def["name"] if "schema_de" in locals() else "N/A"
            logger.info(f"- {action} existing schema: {schema_name} (ID: {schema_id})")

        # Test summary
        if test_created:
            action = "Would create" if dry_run else "Created"
            logger.info(f"- {action} test: {test['name']} (ID: {test['id']})")
        else:
            action = "Would use" if dry_run else "Using"
            logger.info(f"- {action} existing test: {test['name']} (ID: {test['id']})")
        logger.info(f"- Labels created: {len(created_labels)}")
        logger.info(f"- Labels skipped (already exist): {len(skipped_labels)}")
        logger.error(f"- Labels failed: {len(failed_labels)}")

        # Label removal summary
        if dry_run and removed_labels:
            logger.info(f"- Labels would be removed: {len(removed_labels)}")
        elif not dry_run and removed_labels:
            logger.info(f"- Labels removed: {len(removed_labels)}")
        else:
            logger.info(f"- Labels removed: {len(removed_labels)}")

        logger.info(f"- Total labels processed: {len(label_defs)}")

        if failed_labels:
            logger.error("\nFailed labels:")
            for name, error in failed_labels:
                logger.error(f"  - {name}: {error}")

        # Create change detection variables
        logger.info("\nCreating change detection variables...")
        try:
            # Create change detection variables (one per label)
            variable_defs_raw = create_change_detection_variables(
                test["id"], fields, config
            )

            # IMPORTANT: Remove duplicates from generated variables
            # This fixes the counting discrepancy issue
            seen_names = set()
            variable_defs = []
            duplicates_found = []

            for var_def in variable_defs_raw:
                var_name = var_def["name"]
                if var_name in seen_names:
                    duplicates_found.append(var_name)
                    logger.warning(
                        f"Duplicate variable detected: {var_name} (removing duplicate)"
                    )
                else:
                    seen_names.add(var_name)
                    variable_defs.append(var_def)

            logger.info(
                f"Generated {len(variable_defs_raw)} variable definitions ({len(duplicates_found)} duplicates removed)"
            )
            logger.info(f"Unique variables to process: {len(variable_defs)}")

            if duplicates_found:
                logger.warning(
                    f"Removed {len(duplicates_found)} duplicate variables: {', '.join(duplicates_found)}"
                )

            # Log all unique variables
            logger.info("\nUnique change detection variables generated:")
            for i, var_def in enumerate(variable_defs, 1):
                logger.info(f"  {i:2d}. {var_def['name']} (group: {var_def['group']})")

            # Get existing variables to check for duplicates
            try:
                existing_variables = api.get_test_variables(test["id"])
                existing_variable_names = {
                    var.get("name") for var in existing_variables
                }
                logger.info(
                    f"\nFound {len(existing_variables)} existing variables in Horreum"
                )
            except Exception as e:
                logger.warning(
                    f"Warning: Could not retrieve existing variables, will attempt to create all: {e}"
                )
                existing_variables = []  # Initialize as empty list if retrieval fails
                existing_variable_names = set()

            # Separate existing and new variables
            new_variables = []
            skipped_variables = []

            logger.info("\nComparing generated variables with existing variables...")

            for variable_def in variable_defs:
                variable_name = variable_def["name"]
                if variable_name in existing_variable_names:
                    skipped_variables.append(variable_name)
                    logger.info(f"  ✓ {variable_name} (already exists)")
                else:
                    new_variables.append(variable_def)
                    logger.info(f"  + {variable_name} (NEW - will be created)")

            # Create variables: merge existing + new to preserve all existing variables
            created_variables = []
            failed_variables = []

            logger.info("\n=== VARIABLE CREATION SUMMARY ===")
            logger.info(f"Generated from config: {len(variable_defs)} unique variables")
            logger.info(f"Already exist in Horreum: {len(skipped_variables)} variables")
            logger.info(f"New variables to create: {len(new_variables)} variables")

            if new_variables:
                logger.info("\nNEW VARIABLES TO CREATE:")
                for i, var in enumerate(new_variables, 1):
                    logger.info(f"  {i}. {var['name']} (group: {var['group']})")

                action = "[DRY RUN] Would create" if dry_run else "Creating"
                logger.info(
                    f"\n{action} {len(new_variables)} new variables while preserving "
                    f"{len(existing_variables)} existing..."
                )

                if not dry_run:
                    try:
                        # CRITICAL FIX: Merge existing + new variables
                        # The API replaces ALL variables, so we must send the complete list
                        all_variables = existing_variables + new_variables

                        result = api.create_multiple_change_detection_variables(
                            test["id"], all_variables
                        )
                        created_variables = (
                            new_variables  # Track only the newly added ones
                        )
                        logger.info(
                            f"Successfully updated variable list: {len(existing_variables)} existing + "
                            f"{len(new_variables)} new = {len(all_variables)} total"
                        )

                        # Verify final state
                        final_variables = api.get_test_variables(test["id"])
                        logger.info(
                            f"Total variables now in system: {len(final_variables)}"
                        )

                    except Exception as e:
                        logger.error(f"Variable update failed: {e}")
                        failed_variables = [
                            (var["name"], str(e)) for var in new_variables
                        ]
                else:
                    # In dry-run mode
                    logger.info(
                        f"[DRY RUN] Would update variable list with {len(new_variables)} new variables"
                    )
                    created_variables = []  # Don't count as created in dry-run
            else:
                logger.info(
                    "\n✓ All desired variables already exist - no changes needed"
                )

            logger.info("\n=== CHANGE DETECTION SUMMARY ===")

            # Show clear breakdown
            if dry_run:
                logger.info(f"- Variables that would be created: {len(new_variables)}")
                logger.info(
                    f"- Variables skipped (already exist): {len(skipped_variables)}"
                )
            else:
                logger.info(f"- Variables created: {len(created_variables)}")
                logger.info(
                    f"- Variables skipped (already exist): {len(skipped_variables)}"
                )

            logger.error(f"- Variables failed: {len(failed_variables)}")

            # Show any extra variables in Horreum not in config
            expected_variable_names = {var["name"] for var in variable_defs}
            extra_variables = existing_variable_names - expected_variable_names
            if extra_variables:
                logger.info(
                    f"- Extra variables in Horreum (not in config): {len(extra_variables)}"
                )
                logger.info(f"  Extra variables: {', '.join(sorted(extra_variables))}")

            # Variable removal summary
            if dry_run and removed_variables:
                logger.info(f"- Variables would be removed: {len(removed_variables)}")
            elif not dry_run and removed_variables:
                logger.info(f"- Variables removed: {len(removed_variables)}")
            else:
                logger.info(f"- Variables removed: {len(removed_variables)}")

            logger.info(f"- Total unique variables processed: {len(variable_defs)}")

            # Final accounting
            expected_total = len(skipped_variables) + len(new_variables)
            if expected_total != len(variable_defs):
                logger.warning(
                    f"⚠️  Accounting mismatch: {len(skipped_variables)} + {len(new_variables)} != {len(variable_defs)}"
                )
            else:
                logger.info(
                    f"✓ Accounting verified: {len(skipped_variables)} existing + {len(new_variables)} new = {len(variable_defs)} total"
                )

            if failed_variables:
                logger.error("\n❌ FAILED VARIABLES:")
                for i, (name, error) in enumerate(failed_variables, 1):
                    logger.error(f"  {i}. {name}: {error}")

        except Exception as e:
            logger.error(f"Error creating change detection variables: {e}")
            # Continue anyway - this is not critical to basic functionality
            created_variables = []
            skipped_variables = []
            failed_variables = []
            variable_defs = []  # Initialize for cleanup section

        # Cleanup variables that are no longer in configuration
        cleanup_variables = (
            os.getenv("CLEANUP_VARIABLES", "true").lower() == "true"
        )  # Default: cleanup enabled

        if cleanup_variables:
            logger.info("\nCleaning up obsolete change detection variables...")
            try:
                # Get current variables and compare with configuration
                current_variables = api.get_test_variables(test["id"])
                current_variable_names = {var.get("name") for var in current_variables}

                # Get expected variables from configuration
                expected_variable_names = {
                    field["label_name"]
                    for field in fields
                    if field.get("change_detection_group")
                }

                # Find variables to remove (exist in Horreum but not in config)
                variables_to_remove = current_variable_names - expected_variable_names

                if variables_to_remove:
                    action = "Would remove" if dry_run else "Found"
                    suffix = "to remove" if dry_run else ""
                    logger.info(
                        f"{action} {len(variables_to_remove)} obsolete variables {suffix}:"
                    )
                    for variable_name in variables_to_remove:
                        logger.info(f"  - {variable_name}")

                    if dry_run:
                        # In dry-run mode, just count what would be removed
                        removed_variables.extend(variables_to_remove)
                        logger.info(
                            f"[DRY RUN] Would remove {len(variables_to_remove)} obsolete variables"
                        )
                    else:
                        # Actually remove obsolete variables
                        for variable in current_variables:
                            variable_name = variable.get("name")
                            variable_id = variable.get("id")

                            if variable_name in variables_to_remove:
                                if api.delete_variable(variable_id):
                                    removed_variables.append(variable_name)
                                    logger.info(f"Removed variable: {variable_name}")
                                else:
                                    logger.error(
                                        f"Failed to remove variable: {variable_name}"
                                    )
                else:
                    action = "Would find" if dry_run else ""
                    logger.info(f"{action} No obsolete variables found")

            except Exception as e:
                logger.error(f"Variable cleanup failed: {e}")
        else:
            logger.info(
                "Variable cleanup disabled (set CLEANUP_VARIABLES=true to enable)"
            )

        # Synchronize server variable change detection configs with YAML
        try:
            sync_change_detection_configs(api, test["id"], fields, config)
        except Exception as e:
            logger.error(f"Sync of change detection configs failed: {e}")

        # Save configuration for reference
        output_config = {
            "schema_id": schema_id,
            "test_id": test["id"],
            "test_name": test["name"],
            "schema_uri": schema_def["uri"],  # uri is now mandatory
            "labels_created": len(created_labels),
            "labels_skipped": len(skipped_labels),
            "labels_failed": len(failed_labels),
            "labels_removed": len(removed_labels),
            "variables_created": (
                len(created_variables) if "created_variables" in locals() else 0
            ),
            "variables_skipped": (
                len(skipped_variables) if "skipped_variables" in locals() else 0
            ),
            "variables_failed": (
                len(failed_variables) if "failed_variables" in locals() else 0
            ),
            "variables_removed": len(removed_variables),
            "change_detection_groups": list(
                config.get("change_detection_groups", {}).keys()
            ),
            "fields": fields,
        }

        with open("horreum_config.json", "w") as f:
            json.dump(output_config, f, indent=2)

        logger.info("\nConfiguration saved to horreum_config.json")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
