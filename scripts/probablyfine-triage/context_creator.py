#!/usr/bin/env python3
"""Create .probablyfine/context.json from guided human input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_CONTEXT: Dict[str, Any] = {
    "schema_version": "0.1.0",
    "component": {
        "name": "probablyfine",
        "type": "service",
        "runtime": "container",
        "orchestrator": "kubernetes",
        "cloud": "aws",
        "platform": "eks",
        "namespace": "prod",
        "exposure": "internal",
    },
    "network": {
        "internet_ingress": {
            "public_entrypoint": True,
            "unrestricted": False,
            "fronted_by": ["nginx"],
            "authn": "required",
            "authz": "required",
            "rate_limited": True,
            "waf": "unknown",
            "mTLS": "unknown",
        },
        "service_reachability": {
            "reachable_from_internet_directly": False,
            "reachable_via_public_ingress": True,
            "reachable_from_same_vpc": True,
            "reachable_only_from_cluster": False,
        },
        "allowed_endpoints": [
            {"method": "GET", "path": "/healthz", "purpose": "healthcheck"},
            {"method": "POST", "path": "/api/v1/thing", "purpose": "business"},
        ],
        "default_deny": True,
    },
    "auth_boundary": {
        "internet_to_ingress": "strong",
        "ingress_to_service": "unknown",
        "service_requires_auth": True,
        "auth_type": ["oidc", "jwt"],
        "privilege_required": "user",
    },
    "data": {
        "confidentiality_requirement": "high",
        "integrity_requirement": "medium",
        "availability_requirement": "medium",
    },
    "controls": {
        "reverse_proxy_hardened": True,
        "input_validation_at_edge": "unknown",
        "egress_restricted": "unknown",
        "pod_security": "unknown",
        "network_policy_enforced": "unknown",
    },
}


def read_input(prompt: str) -> str:
    return input(prompt).strip()


def ask_text(label: str, default: str, non_interactive: bool) -> str:
    if non_interactive:
        return default
    value = read_input(f"{label} [{default}]: ")
    return value if value else default


def ask_choice(label: str, options: List[str], default: str, non_interactive: bool) -> str:
    normalized = {opt.lower(): opt for opt in options}
    if default.lower() not in normalized:
        raise ValueError(f"Default '{default}' not in options for '{label}'")

    if non_interactive:
        return normalized[default.lower()]

    while True:
        joined = "/".join(options)
        value = read_input(f"{label} ({joined}) [{default}]: ")
        if not value:
            return normalized[default.lower()]
        key = value.lower()
        if key in normalized:
            return normalized[key]
        print(f"Invalid value. Expected one of: {joined}")


def ask_bool(label: str, default: bool, non_interactive: bool) -> bool:
    default_token = "y" if default else "n"
    if non_interactive:
        return default

    while True:
        value = read_input(f"{label} (y/n) [{default_token}]: ").lower()
        if not value:
            return default
        if value in {"y", "yes", "true", "1"}:
            return True
        if value in {"n", "no", "false", "0"}:
            return False
        print("Invalid value. Enter y or n.")


def ask_tri_bool(label: str, default: Any, non_interactive: bool) -> Any:
    if default is True:
        default_token = "yes"
    elif default is False:
        default_token = "no"
    else:
        default_token = "unknown"

    value = ask_choice(label, ["yes", "no", "unknown"], default_token, non_interactive)
    if value == "yes":
        return True
    if value == "no":
        return False
    return "unknown"


def ask_list(label: str, default: List[str], non_interactive: bool) -> List[str]:
    if non_interactive:
        return default

    default_display = ",".join(default)
    raw = read_input(f"{label} (comma-separated) [{default_display}]: ")
    if not raw:
        return default
    out = [part.strip() for part in raw.split(",") if part.strip()]
    return out if out else default


def ask_int(label: str, default: int, min_value: int, max_value: int, non_interactive: bool) -> int:
    if non_interactive:
        return default

    while True:
        value = read_input(f"{label} [{default}]: ")
        if not value:
            return default
        try:
            parsed = int(value)
        except ValueError:
            print("Invalid integer.")
            continue
        if parsed < min_value or parsed > max_value:
            print(f"Out of range. Expected {min_value}..{max_value}.")
            continue
        return parsed


def build_context(non_interactive: bool) -> Dict[str, Any]:
    d = DEFAULT_CONTEXT

    component = {
        "name": ask_text("Component name", d["component"]["name"], non_interactive),
        "type": ask_choice(
            "Component type",
            ["service", "library", "batch", "worker", "other"],
            d["component"]["type"],
            non_interactive,
        ),
        "runtime": ask_choice(
            "Runtime model",
            ["container", "vm", "serverless", "bare-metal", "unknown"],
            d["component"]["runtime"],
            non_interactive,
        ),
        "orchestrator": ask_choice(
            "Orchestrator",
            ["kubernetes", "ecs", "nomad", "none", "unknown"],
            d["component"]["orchestrator"],
            non_interactive,
        ),
        "cloud": ask_choice(
            "Cloud provider",
            ["aws", "gcp", "azure", "on-prem", "unknown"],
            d["component"]["cloud"],
            non_interactive,
        ),
        "platform": ask_text("Platform", d["component"]["platform"], non_interactive),
        "namespace": ask_text("Namespace/environment", d["component"]["namespace"], non_interactive),
        "exposure": ask_choice(
            "Exposure",
            ["internal", "public", "unknown"],
            d["component"]["exposure"],
            non_interactive,
        ),
    }

    ingress_defaults = d["network"]["internet_ingress"]
    reach_defaults = d["network"]["service_reachability"]

    internet_ingress = {
        "public_entrypoint": ask_bool("Public entrypoint exists", ingress_defaults["public_entrypoint"], non_interactive),
        "unrestricted": ask_bool("Unrestricted public access", ingress_defaults["unrestricted"], non_interactive),
        "fronted_by": ask_list("Ingress fronted by", ingress_defaults["fronted_by"], non_interactive),
        "authn": ask_choice(
            "Ingress authentication",
            ["required", "not-required", "unknown"],
            ingress_defaults["authn"],
            non_interactive,
        ),
        "authz": ask_choice(
            "Ingress authorization",
            ["required", "not-required", "unknown"],
            ingress_defaults["authz"],
            non_interactive,
        ),
        "rate_limited": ask_bool("Ingress rate-limited", ingress_defaults["rate_limited"], non_interactive),
        "waf": ask_tri_bool("WAF enabled", ingress_defaults["waf"], non_interactive),
        "mTLS": ask_tri_bool("mTLS enabled", ingress_defaults["mTLS"], non_interactive),
    }

    service_reachability = {
        "reachable_from_internet_directly": ask_bool(
            "Service directly reachable from internet",
            reach_defaults["reachable_from_internet_directly"],
            non_interactive,
        ),
        "reachable_via_public_ingress": ask_bool(
            "Service reachable via public ingress",
            reach_defaults["reachable_via_public_ingress"],
            non_interactive,
        ),
        "reachable_from_same_vpc": ask_bool(
            "Service reachable from same VPC",
            reach_defaults["reachable_from_same_vpc"],
            non_interactive,
        ),
        "reachable_only_from_cluster": ask_bool(
            "Service reachable only from cluster",
            reach_defaults["reachable_only_from_cluster"],
            non_interactive,
        ),
    }

    endpoint_defaults = d["network"]["allowed_endpoints"]
    endpoint_count = ask_int("Number of allowed endpoints", len(endpoint_defaults), 0, 50, non_interactive)
    allowed_endpoints: List[Dict[str, str]] = []
    for i in range(endpoint_count):
        base = endpoint_defaults[i] if i < len(endpoint_defaults) else {"method": "GET", "path": "/", "purpose": "unknown"}
        allowed_endpoints.append(
            {
                "method": ask_text(f"Endpoint {i + 1} method", str(base["method"]).upper(), non_interactive).upper(),
                "path": ask_text(f"Endpoint {i + 1} path", str(base["path"]), non_interactive),
                "purpose": ask_text(f"Endpoint {i + 1} purpose", str(base["purpose"]), non_interactive),
            }
        )

    network = {
        "internet_ingress": internet_ingress,
        "service_reachability": service_reachability,
        "allowed_endpoints": allowed_endpoints,
        "default_deny": ask_bool("Default deny network policy", d["network"]["default_deny"], non_interactive),
    }

    auth_defaults = d["auth_boundary"]
    auth_boundary = {
        "internet_to_ingress": ask_choice(
            "Internet->ingress boundary",
            ["strong", "weak", "none", "unknown"],
            auth_defaults["internet_to_ingress"],
            non_interactive,
        ),
        "ingress_to_service": ask_choice(
            "Ingress->service boundary",
            ["strong", "weak", "none", "unknown"],
            auth_defaults["ingress_to_service"],
            non_interactive,
        ),
        "service_requires_auth": ask_bool(
            "Service requires auth",
            auth_defaults["service_requires_auth"],
            non_interactive,
        ),
        "auth_type": ask_list("Auth types", auth_defaults["auth_type"], non_interactive),
        "privilege_required": ask_choice(
            "Privilege required",
            ["none", "user", "service", "admin", "unknown"],
            auth_defaults["privilege_required"],
            non_interactive,
        ),
    }

    data_defaults = d["data"]
    data = {
        "confidentiality_requirement": ask_choice(
            "Confidentiality requirement",
            ["high", "medium", "low", "unknown"],
            data_defaults["confidentiality_requirement"],
            non_interactive,
        ),
        "integrity_requirement": ask_choice(
            "Integrity requirement",
            ["high", "medium", "low", "unknown"],
            data_defaults["integrity_requirement"],
            non_interactive,
        ),
        "availability_requirement": ask_choice(
            "Availability requirement",
            ["high", "medium", "low", "unknown"],
            data_defaults["availability_requirement"],
            non_interactive,
        ),
    }

    controls_defaults = d["controls"]
    controls = {
        "reverse_proxy_hardened": ask_bool(
            "Reverse proxy hardened",
            controls_defaults["reverse_proxy_hardened"],
            non_interactive,
        ),
        "input_validation_at_edge": ask_tri_bool(
            "Input validation at edge",
            controls_defaults["input_validation_at_edge"],
            non_interactive,
        ),
        "egress_restricted": ask_tri_bool(
            "Egress restricted",
            controls_defaults["egress_restricted"],
            non_interactive,
        ),
        "pod_security": ask_tri_bool(
            "Pod security enforced",
            controls_defaults["pod_security"],
            non_interactive,
        ),
        "network_policy_enforced": ask_tri_bool(
            "Network policy enforced",
            controls_defaults["network_policy_enforced"],
            non_interactive,
        ),
    }

    return {
        "schema_version": d["schema_version"],
        "component": component,
        "network": network,
        "auth_boundary": auth_boundary,
        "data": data,
        "controls": controls,
    }


def write_context(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".probablyfine/context.json"))
    parser.add_argument("--non-interactive", action="store_true", help="Write default starter context without prompts")
    parser.add_argument("--force", action="store_true", help="Overwrite output file if it already exists")
    args = parser.parse_args()

    if args.output.exists() and not args.force:
        if args.non_interactive:
            raise SystemExit(f"Refusing to overwrite existing file: {args.output}. Use --force.")

        overwrite = ask_bool(f"{args.output} exists. Overwrite", False, non_interactive=False)
        if not overwrite:
            raise SystemExit("Aborted by user.")

    payload = build_context(non_interactive=args.non_interactive)
    write_context(args.output, payload)
    print(f"Wrote context: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
