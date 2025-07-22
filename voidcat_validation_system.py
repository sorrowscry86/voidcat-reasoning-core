#!/usr/bin/env python3
"""
VoidCat Comprehensive Validation System - Pillar IV Infrastructure Component

This module implements comprehensive validation mechanisms for the VoidCat enhanced MCP server
ensuring data integrity, security, input validation, and operational safety across all components.

Features:
- Multi-layer input validation with schema enforcement
- Data integrity validation across components
- Security validation and threat detection
- Configuration validation and consistency checks
- Cross-component validation and dependency verification
- Performance validation and resource monitoring
- Real-time validation monitoring and reporting
- Integration with logging and audit systems

Author: VoidCat Reasoning Core Team - Pillar IV Infrastructure
License: MIT
Version: 1.0.0
"""

import hashlib
import ipaddress
import json
import os
import re
import time
import urllib.parse
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# Validation levels and categories
class ValidationLevel(Enum):
    """Validation strictness levels."""

    PERMISSIVE = "permissive"  # Basic validation only
    STANDARD = "standard"  # Standard validation rules
    STRICT = "strict"  # Strict validation with enhanced security
    PARANOID = "paranoid"  # Maximum validation and security


class ValidationType(Enum):
    """Types of validation performed."""

    INPUT = "input"  # Input parameter validation
    DATA_INTEGRITY = "data_integrity"  # Data consistency validation
    SECURITY = "security"  # Security and threat validation
    SCHEMA = "schema"  # Schema compliance validation
    CONFIGURATION = "configuration"  # Configuration validation
    PERFORMANCE = "performance"  # Performance and resource validation
    CROSS_COMPONENT = "cross_component"  # Inter-component validation
    BUSINESS_LOGIC = "business_logic"  # Business rule validation


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    validation_type: ValidationType
    validator_name: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "validation_type": self.validation_type.value,
            "validator_name": self.validator_name,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "validation_id": self.validation_id,
        }


@dataclass
class ValidationRule:
    """Definition of a validation rule."""

    name: str
    description: str
    validation_type: ValidationType
    validator_function: Callable
    enabled: bool = True
    severity: str = "error"
    conditions: Dict[str, Any] = field(default_factory=dict)


class VoidCatValidator:
    """
    Comprehensive validation system for VoidCat with multi-layer validation,
    security checks, and data integrity verification.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the VoidCat validation system.

        Args:
            config: Validation configuration dictionary
        """
        self.config = config or {}
        self.validation_level = ValidationLevel(
            self.config.get("validation_level", "standard")
        )

        # Validation rules registry
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self.validation_stats = defaultdict(int)

        # Security patterns and rules
        self.security_patterns = self._initialize_security_patterns()
        self.sensitive_fields = self._initialize_sensitive_fields()

        # Performance thresholds
        self.performance_thresholds = self._initialize_performance_thresholds()

        # Initialize validation rules
        self._register_core_validators()

        # Setup logging integration
        try:
            from voidcat_logging_system import LogCategory, get_logger

            self.logger = get_logger()
            self.log_category = LogCategory.SECURITY
        except ImportError:
            self.logger = None

        self._log_info("VoidCat comprehensive validation system initialized")

    def _log_info(self, message: str, **kwargs):
        """Log information with fallback."""
        if self.logger:
            self.logger.info(
                message, category=self.log_category, component="validator", **kwargs
            )
        else:
            print(f"[Validator] {message}")

    def _log_error(self, message: str, **kwargs):
        """Log error with fallback."""
        if self.logger:
            self.logger.error(
                message, category=self.log_category, component="validator", **kwargs
            )
        else:
            print(f"[Validator Error] {message}")

    def _initialize_security_patterns(self) -> Dict[str, List[str]]:
        """Initialize security threat detection patterns."""
        return {
            "sql_injection": [
                r"(\b(select|insert|update|delete|drop|create|alter|exec|execute)\b)",
                r"(union\s+select)",
                r"(or\s+1\s*=\s*1)",
                r"(and\s+1\s*=\s*1)",
                r"(\/\*|\*\/|--|\#)",
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*=",
            ],
            "command_injection": [
                r"(\||&|;|`|\$\(|\${)",
                r"(rm\s+-rf|del\s+/)",
                r"(wget|curl)\s+",
                r"(bash|sh|cmd|powershell)\s+",
            ],
            "path_traversal": [
                r"\.\.\/",
                r"\.\.\\",
                r"\/etc\/passwd",
                r"\/proc\/",
                r"\\windows\\system32",
            ],
            "code_injection": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"subprocess\.",
                r"os\.system",
                r"__import__",
            ],
        }

    def _initialize_sensitive_fields(self) -> Set[str]:
        """Initialize list of sensitive field names."""
        return {
            "password",
            "passwd",
            "pwd",
            "secret",
            "key",
            "token",
            "api_key",
            "auth",
            "credential",
            "private",
            "confidential",
            "ssn",
            "social_security",
            "credit_card",
            "card_number",
            "email",
            "phone",
            "address",
            "location",
            "ip_address",
        }

    def _initialize_performance_thresholds(self) -> Dict[str, Any]:
        """Initialize performance validation thresholds."""
        return {
            "max_request_size_mb": 100,
            "max_response_time_seconds": 30,
            "max_memory_usage_mb": 1000,
            "max_file_size_mb": 50,
            "max_batch_size": 1000,
            "max_recursion_depth": 100,
        }

    def _register_core_validators(self) -> None:
        """Register core validation rules."""
        # Input validation rules
        self.register_validator(
            "input_required_fields",
            "Validate that required fields are present",
            ValidationType.INPUT,
            self._validate_required_fields,
        )

        self.register_validator(
            "input_data_types",
            "Validate data types match schema",
            ValidationType.INPUT,
            self._validate_data_types,
        )

        self.register_validator(
            "input_string_lengths",
            "Validate string length constraints",
            ValidationType.INPUT,
            self._validate_string_lengths,
        )

        self.register_validator(
            "input_numeric_ranges",
            "Validate numeric values are within acceptable ranges",
            ValidationType.INPUT,
            self._validate_numeric_ranges,
        )

        # Security validation rules
        self.register_validator(
            "security_injection_detection",
            "Detect potential injection attacks",
            ValidationType.SECURITY,
            self._validate_injection_detection,
            severity="critical",
        )

        self.register_validator(
            "security_file_paths",
            "Validate file paths for security",
            ValidationType.SECURITY,
            self._validate_file_paths,
            severity="error",
        )

        self.register_validator(
            "security_sensitive_data",
            "Validate handling of sensitive data",
            ValidationType.SECURITY,
            self._validate_sensitive_data,
            severity="warning",
        )

        # Data integrity rules
        self.register_validator(
            "data_integrity_checksums",
            "Validate data integrity using checksums",
            ValidationType.DATA_INTEGRITY,
            self._validate_data_checksums,
        )

        self.register_validator(
            "data_integrity_references",
            "Validate referential integrity",
            ValidationType.DATA_INTEGRITY,
            self._validate_referential_integrity,
        )

        # Configuration validation rules
        self.register_validator(
            "config_required_settings",
            "Validate required configuration settings",
            ValidationType.CONFIGURATION,
            self._validate_config_settings,
        )

        # Performance validation rules
        self.register_validator(
            "performance_resource_usage",
            "Validate resource usage is within limits",
            ValidationType.PERFORMANCE,
            self._validate_resource_usage,
        )

    def register_validator(
        self,
        name: str,
        description: str,
        validation_type: ValidationType,
        validator_function: Callable,
        severity: str = "error",
        conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a new validation rule.

        Args:
            name: Unique name for the validator
            description: Human-readable description
            validation_type: Type of validation
            validator_function: Function that performs validation
            severity: Severity level for failures
            conditions: Conditions when this validator applies
        """
        rule = ValidationRule(
            name=name,
            description=description,
            validation_type=validation_type,
            validator_function=validator_function,
            severity=severity,
            conditions=conditions or {},
        )

        self.validation_rules[name] = rule
        self._log_info(f"Registered validator: {name}")

    def validate(
        self,
        data: Any,
        context: Optional[Dict[str, Any]] = None,
        validation_types: Optional[List[ValidationType]] = None,
    ) -> List[ValidationResult]:
        """
        Perform comprehensive validation on data.

        Args:
            data: Data to validate
            context: Validation context (schemas, rules, etc.)
            validation_types: Specific validation types to run

        Returns:
            List[ValidationResult]: Results of all validations
        """
        context = context or {}
        validation_types = validation_types or list(ValidationType)

        results = []

        # Run applicable validators
        for rule_name, rule in self.validation_rules.items():
            if not rule.enabled:
                continue

            if rule.validation_type not in validation_types:
                continue

            # Check if rule conditions are met
            if not self._check_rule_conditions(rule, data, context):
                continue

            try:
                result = rule.validator_function(data, context, rule)
                if result:
                    results.append(result)
                    self.validation_history.append(result)
                    self.validation_stats[rule.validation_type] += 1

                    if not result.is_valid:
                        self._log_error(
                            f"Validation failed: {rule_name}", details=result.details
                        )

            except Exception as e:
                error_result = ValidationResult(
                    is_valid=False,
                    validation_type=rule.validation_type,
                    validator_name=rule_name,
                    message=f"Validator error: {str(e)}",
                    severity="critical",
                    details={"exception": str(e)},
                )
                results.append(error_result)
                self._log_error(f"Validator {rule_name} failed with exception: {e}")

        return results

    def _check_rule_conditions(
        self, rule: ValidationRule, data: Any, context: Dict[str, Any]
    ) -> bool:
        """Check if rule conditions are satisfied."""
        if not rule.conditions:
            return True

        # Check validation level requirements
        if "min_validation_level" in rule.conditions:
            required_level = ValidationLevel(rule.conditions["min_validation_level"])
            level_priority = {
                ValidationLevel.PERMISSIVE: 1,
                ValidationLevel.STANDARD: 2,
                ValidationLevel.STRICT: 3,
                ValidationLevel.PARANOID: 4,
            }
            if level_priority[self.validation_level] < level_priority[required_level]:
                return False

        # Check context requirements
        if "required_context" in rule.conditions:
            for key in rule.conditions["required_context"]:
                if key not in context:
                    return False

        return True

    # Core validator implementations
    def _validate_required_fields(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate that required fields are present."""
        schema = context.get("schema", {})
        required_fields = schema.get("required", [])

        if not required_fields or not isinstance(data, dict):
            return None

        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields},
                severity=rule.severity,
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="All required fields present",
            details={"required_fields_count": len(required_fields)},
        )

    def _validate_data_types(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate data types match schema."""
        schema = context.get("schema", {})
        properties = schema.get("properties", {})

        if not properties or not isinstance(data, dict):
            return None

        type_errors = []
        for field, field_schema in properties.items():
            if field not in data:
                continue

            expected_type = field_schema.get("type")
            if not expected_type:
                continue

            value = data[field]
            if not self._check_type(value, expected_type):
                type_errors.append(
                    {
                        "field": field,
                        "expected_type": expected_type,
                        "actual_type": type(value).__name__,
                    }
                )

        if type_errors:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Type validation failed for {len(type_errors)} fields",
                details={"type_errors": type_errors},
                severity=rule.severity,
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="All data types valid",
        )

    def _validate_string_lengths(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate string length constraints."""
        schema = context.get("schema", {})
        properties = schema.get("properties", {})

        if not properties or not isinstance(data, dict):
            return None

        length_errors = []
        for field, field_schema in properties.items():
            if field not in data or not isinstance(data[field], str):
                continue

            value = data[field]
            min_length = field_schema.get("minLength")
            max_length = field_schema.get("maxLength")

            if min_length is not None and len(value) < min_length:
                length_errors.append(
                    {
                        "field": field,
                        "constraint": "minLength",
                        "expected": min_length,
                        "actual": len(value),
                    }
                )

            if max_length is not None and len(value) > max_length:
                length_errors.append(
                    {
                        "field": field,
                        "constraint": "maxLength",
                        "expected": max_length,
                        "actual": len(value),
                    }
                )

        if length_errors:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"String length validation failed for {len(length_errors)} fields",
                details={"length_errors": length_errors},
                severity=rule.severity,
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="All string lengths valid",
        )

    def _validate_numeric_ranges(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate numeric values are within acceptable ranges."""
        schema = context.get("schema", {})
        properties = schema.get("properties", {})

        if not properties or not isinstance(data, dict):
            return None

        range_errors = []
        for field, field_schema in properties.items():
            if field not in data:
                continue

            value = data[field]
            if not isinstance(value, (int, float)):
                continue

            minimum = field_schema.get("minimum")
            maximum = field_schema.get("maximum")

            if minimum is not None and value < minimum:
                range_errors.append(
                    {
                        "field": field,
                        "constraint": "minimum",
                        "expected": minimum,
                        "actual": value,
                    }
                )

            if maximum is not None and value > maximum:
                range_errors.append(
                    {
                        "field": field,
                        "constraint": "maximum",
                        "expected": maximum,
                        "actual": value,
                    }
                )

        if range_errors:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Numeric range validation failed for {len(range_errors)} fields",
                details={"range_errors": range_errors},
                severity=rule.severity,
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="All numeric ranges valid",
        )

    def _validate_injection_detection(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Detect potential injection attacks."""
        if not isinstance(data, (str, dict)):
            return None

        threats_detected = []

        def check_string_for_threats(text: str, field_name: str = ""):
            for threat_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        threats_detected.append(
                            {
                                "threat_type": threat_type,
                                "field": field_name,
                                "pattern_matched": pattern,
                                "suspicious_text": (
                                    text[:100] + "..." if len(text) > 100 else text
                                ),
                            }
                        )

        if isinstance(data, str):
            check_string_for_threats(data)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    check_string_for_threats(value, key)
                elif isinstance(value, dict):
                    # Recursively check nested dictionaries
                    nested_result = self._validate_injection_detection(
                        value, context, rule
                    )
                    if nested_result and not nested_result.is_valid:
                        threats_detected.extend(
                            nested_result.details.get("threats_detected", [])
                        )

        if threats_detected:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Potential security threats detected: {len(threats_detected)} issues",
                details={"threats_detected": threats_detected},
                severity="critical",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="No security threats detected",
        )

    def _validate_file_paths(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate file paths for security."""
        if not isinstance(data, (str, dict)):
            return None

        path_issues = []

        def check_path_security(path: str, field_name: str = ""):
            # Check for path traversal
            if ".." in path:
                path_issues.append(
                    {
                        "issue": "path_traversal",
                        "field": field_name,
                        "path": path,
                        "description": "Path contains '..' which may indicate path traversal",
                    }
                )

            # Check for absolute paths to sensitive locations
            sensitive_paths = [
                "/etc/",
                "/proc/",
                "/sys/",
                "C:\\Windows\\",
                "C:\\Program Files\\",
            ]
            for sensitive in sensitive_paths:
                if sensitive.lower() in path.lower():
                    path_issues.append(
                        {
                            "issue": "sensitive_path",
                            "field": field_name,
                            "path": path,
                            "description": f"Path accesses sensitive location: {sensitive}",
                        }
                    )

            # Check for executable extensions
            executable_extensions = [".exe", ".bat", ".cmd", ".ps1", ".sh", ".bash"]
            for ext in executable_extensions:
                if path.lower().endswith(ext):
                    path_issues.append(
                        {
                            "issue": "executable_file",
                            "field": field_name,
                            "path": path,
                            "description": f"Path points to executable file: {ext}",
                        }
                    )

        if isinstance(data, str) and ("/" in data or "\\" in data):
            check_path_security(data)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and ("/" in value or "\\" in value):
                    check_path_security(value, key)

        if path_issues:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"File path security issues detected: {len(path_issues)} issues",
                details={"path_issues": path_issues},
                severity=rule.severity,
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="File paths are secure",
        )

    def _validate_sensitive_data(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate handling of sensitive data."""
        if not isinstance(data, dict):
            return None

        sensitive_data_found = []

        for key, value in data.items():
            key_lower = str(key).lower()

            # Check for sensitive field names
            for sensitive_field in self.sensitive_fields:
                if sensitive_field in key_lower:
                    sensitive_data_found.append(
                        {
                            "field": key,
                            "type": "sensitive_field_name",
                            "pattern_matched": sensitive_field,
                            "recommendation": "Consider encrypting or masking this field",
                        }
                    )

            # Check for patterns that look like sensitive data
            if isinstance(value, str):
                # Check for email patterns
                if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
                    sensitive_data_found.append(
                        {
                            "field": key,
                            "type": "email_address",
                            "recommendation": "Consider data protection measures for email addresses",
                        }
                    )

                # Check for credit card patterns
                if re.match(r"^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$", value):
                    sensitive_data_found.append(
                        {
                            "field": key,
                            "type": "credit_card_pattern",
                            "recommendation": "Credit card data requires PCI DSS compliance",
                        }
                    )

                # Check for SSN patterns
                if re.match(r"^\d{3}-?\d{2}-?\d{4}$", value):
                    sensitive_data_found.append(
                        {
                            "field": key,
                            "type": "ssn_pattern",
                            "recommendation": "SSN data requires special protection measures",
                        }
                    )

        if sensitive_data_found:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Sensitive data detected: {len(sensitive_data_found)} instances",
                details={"sensitive_data": sensitive_data_found},
                severity="warning",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="No sensitive data handling issues detected",
        )

    def _validate_data_checksums(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate data integrity using checksums."""
        expected_checksum = context.get("expected_checksum")
        if not expected_checksum:
            return None

        # Calculate checksum of current data
        data_str = (
            json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
        )
        calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()

        if calculated_checksum != expected_checksum:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message="Data integrity check failed - checksum mismatch",
                details={
                    "expected_checksum": expected_checksum,
                    "calculated_checksum": calculated_checksum,
                },
                severity="error",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="Data integrity verified",
            details={"checksum": calculated_checksum},
        )

    def _validate_referential_integrity(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate referential integrity."""
        references = context.get("references", {})
        if not references or not isinstance(data, dict):
            return None

        broken_references = []

        for field, reference_config in references.items():
            if field not in data:
                continue

            reference_value = data[field]
            reference_type = reference_config.get("type")
            valid_values = reference_config.get("valid_values", [])

            if reference_type == "foreign_key" and reference_value not in valid_values:
                broken_references.append(
                    {
                        "field": field,
                        "value": reference_value,
                        "reference_type": reference_type,
                        "valid_values_count": len(valid_values),
                    }
                )

        if broken_references:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Referential integrity violations: {len(broken_references)} issues",
                details={"broken_references": broken_references},
                severity="error",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="Referential integrity maintained",
        )

    def _validate_config_settings(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate required configuration settings."""
        required_config = context.get("required_config", [])
        if not required_config or not isinstance(data, dict):
            return None

        missing_config = []
        invalid_config = []

        for config_item in required_config:
            name = config_item.get("name")
            required = config_item.get("required", True)
            valid_values = config_item.get("valid_values")

            if required and name not in data:
                missing_config.append(name)
            elif name in data and valid_values:
                if data[name] not in valid_values:
                    invalid_config.append(
                        {
                            "name": name,
                            "value": data[name],
                            "valid_values": valid_values,
                        }
                    )

        issues = []
        if missing_config:
            issues.append(f"Missing configuration: {', '.join(missing_config)}")
        if invalid_config:
            issues.append(f"Invalid configuration values: {len(invalid_config)} items")

        if issues:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message="; ".join(issues),
                details={
                    "missing_config": missing_config,
                    "invalid_config": invalid_config,
                },
                severity="error",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="Configuration validation passed",
        )

    def _validate_resource_usage(
        self, data: Any, context: Dict[str, Any], rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate resource usage is within limits."""
        performance_data = context.get("performance_data", {})
        if not performance_data:
            return None

        violations = []

        # Check against thresholds
        for metric, threshold in self.performance_thresholds.items():
            if metric in performance_data:
                value = performance_data[metric]

                if metric.endswith("_mb") and value > threshold:
                    violations.append(
                        {
                            "metric": metric,
                            "value": value,
                            "threshold": threshold,
                            "unit": "MB",
                        }
                    )
                elif metric.endswith("_seconds") and value > threshold:
                    violations.append(
                        {
                            "metric": metric,
                            "value": value,
                            "threshold": threshold,
                            "unit": "seconds",
                        }
                    )
                elif not metric.endswith(("_mb", "_seconds")) and value > threshold:
                    violations.append(
                        {
                            "metric": metric,
                            "value": value,
                            "threshold": threshold,
                            "unit": "count",
                        }
                    )

        if violations:
            return ValidationResult(
                is_valid=False,
                validation_type=rule.validation_type,
                validator_name=rule.name,
                message=f"Performance threshold violations: {len(violations)} metrics exceeded",
                details={"violations": violations},
                severity="warning",
            )

        return ValidationResult(
            is_valid=True,
            validation_type=rule.validation_type,
            validator_name=rule.name,
            message="Resource usage within acceptable limits",
            details={"metrics_checked": len(performance_data)},
        )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected_python_type = type_mapping.get(expected_type)
        if not expected_python_type:
            return True  # Unknown type, allow it

        return isinstance(value, expected_python_type)

    def validate_mcp_request(self, request: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate an MCP request comprehensively.

        Args:
            request: MCP request dictionary

        Returns:
            List[ValidationResult]: Validation results
        """
        # Basic MCP request schema
        mcp_schema = {
            "type": "object",
            "properties": {
                "jsonrpc": {"type": "string"},
                "method": {"type": "string"},
                "id": {"type": ["string", "number", "null"]},
                "params": {"type": "object"},
            },
            "required": ["jsonrpc", "method"],
        }

        context = {"schema": mcp_schema, "validation_context": "mcp_request"}

        return self.validate(
            request,
            context,
            [ValidationType.INPUT, ValidationType.SCHEMA, ValidationType.SECURITY],
        )

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation system status and statistics."""
        recent_validations = self.validation_history[-100:]  # Last 100 validations

        summary = {
            "validation_system": {
                "status": "operational",
                "validation_level": self.validation_level.value,
                "registered_rules": len(self.validation_rules),
                "total_validations": len(self.validation_history),
            },
            "validation_stats": dict(self.validation_stats),
            "recent_activity": {
                "last_100_validations": len(recent_validations),
                "success_rate": (
                    sum(1 for v in recent_validations if v.is_valid)
                    / len(recent_validations)
                    if recent_validations
                    else 0
                ),
                "critical_issues": sum(
                    1
                    for v in recent_validations
                    if v.severity == "critical" and not v.is_valid
                ),
                "security_checks": sum(
                    1
                    for v in recent_validations
                    if v.validation_type == ValidationType.SECURITY
                ),
            },
            "security_status": {
                "security_patterns": len(self.security_patterns),
                "sensitive_fields_monitored": len(self.sensitive_fields),
                "recent_threats_detected": sum(
                    1
                    for v in recent_validations
                    if v.validation_type == ValidationType.SECURITY and not v.is_valid
                ),
            },
            "performance_thresholds": self.performance_thresholds,
        }

        return summary


# Global validator instance for easy access
_global_validator: Optional[VoidCatValidator] = None


def get_validator() -> VoidCatValidator:
    """Get the global VoidCat validator instance."""
    global _global_validator
    if _global_validator is None:
        _global_validator = VoidCatValidator()
    return _global_validator


def initialize_validation(config: Optional[Dict[str, Any]] = None) -> VoidCatValidator:
    """Initialize the global VoidCat validation system."""
    global _global_validator
    _global_validator = VoidCatValidator(config)
    return _global_validator


# Decorator for automatic validation
def validate_input(
    schema: Dict[str, Any], validation_types: Optional[List[ValidationType]] = None
):
    """
    Decorator for automatic input validation.

    Args:
        schema: JSON schema for validation
        validation_types: Types of validation to perform
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            validator = get_validator()

            # Assume first argument is the data to validate
            if args:
                data = args[0]
                context = {"schema": schema}
                results = validator.validate(data, context, validation_types)

                # Check for validation failures
                failures = [
                    r
                    for r in results
                    if not r.is_valid and r.severity in ["error", "critical"]
                ]
                if failures:
                    raise ValueError(f"Validation failed: {failures[0].message}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Example usage and testing
if __name__ == "__main__":

    def test_validation_system():
        """Test the VoidCat validation system."""
        print("Testing VoidCat Comprehensive Validation System")
        print("=" * 55)

        # Initialize validator
        validator = VoidCatValidator({"validation_level": "strict"})

        # Test data with various issues
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "password": "secret123",
            "query": "SELECT * FROM users WHERE id = 1 OR 1=1",  # SQL injection
        }

        # Test schema
        test_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 50},
                "email": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "password": {"type": "string", "minLength": 8},
            },
            "required": ["name", "email"],
        }

        context = {"schema": test_schema}

        # Run validation
        results = validator.validate(test_data, context)

        print(f"Validation completed: {len(results)} checks performed")
        print()

        for result in results:
            status = "✓ PASS" if result.is_valid else "✗ FAIL"
            print(f"{status} [{result.severity.upper()}] {result.validator_name}")
            print(f"    {result.message}")
            if result.details:
                print(f"    Details: {json.dumps(result.details, indent=6)}")
            print()

        # Get summary
        summary = validator.get_validation_summary()
        print("Validation System Summary:")
        print(json.dumps(summary, indent=2))

    test_validation_system()
