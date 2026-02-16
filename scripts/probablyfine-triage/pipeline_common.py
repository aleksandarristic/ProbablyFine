#!/usr/bin/env python3
"""Shared deterministic helpers for probablyfine-triage pipeline stages."""

from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

EPSS_URL = "https://api.first.org/data/v1/epss"
KEV_REPO_URL = "https://github.com/cisagov/kev-data"
KEV_RAW_URL = (
    "https://raw.githubusercontent.com/cisagov/kev-data/develop/"
    "known_exploited_vulnerabilities.json"
)

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,}", re.IGNORECASE)

SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
THREAT_RANK = {"A": 4, "F": 3, "P": 2, "U": 1, "X": 0}
SOURCE_RANK = {"Both": 3, "ECR-only": 2, "Dependabot-only": 1}
RUNTIME_RANK = {"runtime": 2, "unknown": 1, "build-only": 0}

SEVERITY_SUB = {
    "critical": 1.00,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
    "unknown": 0.10,
}
THREAT_SUB = {"A": 1.00, "F": 0.75, "P": 0.50, "U": 0.25, "X": 0.10}
RUNTIME_SUB = {"runtime": 1.00, "unknown": 0.70, "build-only": 0.30}


@dataclass
class InputFinding:
    source: str
    cve: str
    package: str
    severity: str
    fix_version: Optional[str]
    base_vector: Optional[str]
    evidence: str


@dataclass
class CorrelatedFinding:
    cve: str
    package: str
    sources: set[str] = field(default_factory=set)
    severity: str = "unknown"
    fix_version: Optional[str] = None
    base_vector: Optional[str] = None
    evidence_ids: List[str] = field(default_factory=list)


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Optional[Path]) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def get_in(d: Any, keys: Sequence[str], default: Any = None) -> Any:
    cur = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def norm_severity(value: Any) -> str:
    if not isinstance(value, str):
        return "unknown"
    v = value.strip().lower()
    return v if v in SEVERITY_RANK else "unknown"


def norm_package(value: Any) -> str:
    if not isinstance(value, str):
        return "unknown"
    v = value.strip().lower()
    return v if v else "unknown"


def norm_cve(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    m = CVE_PATTERN.search(value)
    if not m:
        return None
    return m.group(0).upper()


def collect_cves(obj: Any) -> List[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str):
                    c = norm_cve(v)
                    if c:
                        found.add(c)
                elif isinstance(v, (dict, list)):
                    walk(v)
                elif isinstance(k, str):
                    c = norm_cve(k)
                    if c:
                        found.add(c)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            c = norm_cve(node)
            if c:
                found.add(c)

    walk(obj)
    return sorted(found)


def best_fix_version(versions: Iterable[Optional[str]]) -> Optional[str]:
    vals = sorted({v.strip() for v in versions if isinstance(v, str) and v.strip()})
    return vals[0] if vals else None


def extract_dependabot(dependabot: Any) -> List[InputFinding]:
    items = as_list(dependabot)
    if isinstance(dependabot, dict):
        for key in ("alerts", "dependencies", "findings", "vulnerabilities"):
            if isinstance(dependabot.get(key), list):
                items = dependabot[key]
                break

    out: List[InputFinding] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        package = norm_package(
            get_in(item, ["dependency", "package", "name"])
            or get_in(item, ["package", "name"])
            or get_in(item, ["security_vulnerability", "package", "name"])
            or item.get("package")
        )

        severity = norm_severity(
            get_in(item, ["security_vulnerability", "severity"])
            or get_in(item, ["security_advisory", "severity"])
            or item.get("severity")
        )

        fix_version = (
            get_in(item, ["security_vulnerability", "first_patched_version", "identifier"])
            or get_in(item, ["security_vulnerability", "fixed_in_version"])
            or get_in(item, ["fixed_version"])
            or get_in(item, ["first_patched_version", "identifier"])
        )

        base_vector = (
            get_in(item, ["security_advisory", "cvss", "vector_string"])
            or get_in(item, ["cvss", "vectorString"])
            or get_in(item, ["cvss", "vector_string"])
            or item.get("cvss_vector")
        )
        if isinstance(base_vector, str):
            base_vector = base_vector.strip() or None
        else:
            base_vector = None

        evidence = str(item.get("id") or item.get("number") or item.get("html_url") or "unknown")

        cves: set[str] = set()
        for ident in as_list(get_in(item, ["security_advisory", "identifiers"], [])):
            if not isinstance(ident, dict):
                continue
            if str(ident.get("type", "")).upper() == "CVE":
                c = norm_cve(ident.get("value"))
                if c:
                    cves.add(c)

        if not cves:
            cves.update(collect_cves(item))

        for cve in sorted(cves):
            out.append(
                InputFinding(
                    source="Dependabot",
                    cve=cve,
                    package=package,
                    severity=severity,
                    fix_version=fix_version.strip() if isinstance(fix_version, str) and fix_version.strip() else None,
                    base_vector=base_vector,
                    evidence=evidence,
                )
            )
    return out


def extract_ecr(ecr_data: Any) -> List[InputFinding]:
    items = as_list(ecr_data)
    if isinstance(ecr_data, dict):
        for key in ("findings", "results", "vulnerabilities"):
            if isinstance(ecr_data.get(key), list):
                items = ecr_data[key]
                break

    out: List[InputFinding] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        pkg_details = get_in(item, ["packageVulnerabilityDetails"], {})
        vuln_pkgs = as_list(pkg_details.get("vulnerablePackages"))

        package = "unknown"
        fix_versions: List[Optional[str]] = []
        if vuln_pkgs:
            names = [norm_package(p.get("name")) for p in vuln_pkgs if isinstance(p, dict)]
            names = [n for n in names if n != "unknown"]
            package = sorted(set(names))[0] if names else "unknown"
            for p in vuln_pkgs:
                if isinstance(p, dict):
                    fix_versions.append(p.get("fixedInVersion"))

        if package == "unknown":
            package = norm_package(item.get("package") or get_in(item, ["package", "name"]))

        severity = norm_severity(item.get("severity") or pkg_details.get("severity"))

        base_vector = None
        for cvss in as_list(item.get("cvss")):
            if not isinstance(cvss, dict):
                continue
            vec = cvss.get("scoringVector") or cvss.get("vectorString")
            if isinstance(vec, str) and vec.strip():
                base_vector = vec.strip()
                break

        evidence = str(item.get("findingArn") or item.get("name") or item.get("uri") or "unknown")

        cves: set[str] = set()
        c = norm_cve(pkg_details.get("vulnerabilityId") or item.get("cve"))
        if c:
            cves.add(c)
        if not cves:
            cves.update(collect_cves(item))

        fix_version = best_fix_version(fix_versions)

        for cve in sorted(cves):
            out.append(
                InputFinding(
                    source="ECR",
                    cve=cve,
                    package=package,
                    severity=severity,
                    fix_version=fix_version,
                    base_vector=base_vector,
                    evidence=evidence,
                )
            )
    return out


def correlate(findings: Sequence[InputFinding]) -> List[CorrelatedFinding]:
    merged: Dict[Tuple[str, str], CorrelatedFinding] = {}
    for f in findings:
        key = (f.cve, f.package)
        if key not in merged:
            merged[key] = CorrelatedFinding(cve=f.cve, package=f.package)
        current = merged[key]
        current.sources.add(f.source)
        if SEVERITY_RANK[f.severity] > SEVERITY_RANK[current.severity]:
            current.severity = f.severity
        if f.fix_version:
            current.fix_version = best_fix_version([current.fix_version, f.fix_version])
        if not current.base_vector and f.base_vector:
            current.base_vector = f.base_vector
        current.evidence_ids.append(f.evidence or "unknown")

    return sorted(merged.values(), key=lambda x: (x.cve, x.package))


def source_bucket_for_sources(sources: set[str]) -> str:
    if sources == {"Dependabot", "ECR"}:
        return "Both"
    if sources == {"ECR"}:
        return "ECR-only"
    return "Dependabot-only"


def normalized_findings_payload(
    correlated: Sequence[CorrelatedFinding],
    dependabot_present: bool,
    ecr_present: bool,
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for finding in correlated:
        items.append(
            {
                "cve": finding.cve,
                "package": finding.package,
                "severity": finding.severity,
                "fix_version": finding.fix_version,
                "cvss4_base_vector": finding.base_vector,
                "sources": sorted(finding.sources),
                "source_bucket": source_bucket_for_sources(finding.sources),
                "evidence_ids": sorted(set(finding.evidence_ids)),
            }
        )

    return {
        "generated_at": utc_now_iso(),
        "inputs": {
            "dependabot.json": "present" if dependabot_present else "missing",
            "ecr_findings.json": "present" if ecr_present else "missing",
        },
        "items": items,
    }


def http_get_json(url: str, timeout: int = 20) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chunked(seq: Sequence[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(seq), size):
        yield list(seq[i : i + size])


def fetch_epss(cves: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    data: Dict[str, Dict[str, Any]] = {}
    if not cves:
        return data

    for batch in chunked(sorted(set(cves)), 100):
        q = urllib.parse.urlencode({"cve": ",".join(batch)})
        payload = http_get_json(f"{EPSS_URL}?{q}")
        ts = payload.get("access") if isinstance(payload, dict) else None
        for item in as_list(payload.get("data") if isinstance(payload, dict) else []):
            if not isinstance(item, dict):
                continue
            cve = norm_cve(item.get("cve"))
            if not cve:
                continue
            try:
                epss = float(item.get("epss")) if item.get("epss") is not None else None
            except (TypeError, ValueError):
                epss = None
            try:
                percentile = float(item.get("percentile")) if item.get("percentile") is not None else None
            except (TypeError, ValueError):
                percentile = None
            data[cve] = {
                "epss_probability": epss,
                "epss_percentile": percentile,
                "epss_timestamp": ts or "unknown",
            }
    return data


def fetch_kev() -> Dict[str, Dict[str, Any]]:
    payload = http_get_json(KEV_RAW_URL)
    data: Dict[str, Dict[str, Any]] = {}
    for item in as_list(payload.get("vulnerabilities") if isinstance(payload, dict) else []):
        if not isinstance(item, dict):
            continue
        cve = norm_cve(item.get("cveID"))
        if not cve:
            continue
        data[cve] = {
            "cisa_kev_listed": True,
            "kev_date_added": item.get("dateAdded"),
            "kev_due_date": item.get("dueDate"),
        }
    return data


def build_threat_cache(cves: Sequence[str]) -> Dict[str, Any]:
    epss = fetch_epss(cves)
    kev = fetch_kev()

    items: List[Dict[str, Any]] = []
    for cve in sorted(set(cves)):
        e = epss.get(cve, {})
        k = kev.get(cve, {})
        items.append(
            {
                "cve": cve,
                "epss_probability": e.get("epss_probability"),
                "epss_percentile": e.get("epss_percentile"),
                "cisa_kev_listed": bool(k.get("cisa_kev_listed", False)),
                "kev_date_added": k.get("kev_date_added"),
                "kev_due_date": k.get("kev_due_date"),
            }
        )

    return {
        "generated_at": utc_now_iso(),
        "sources": {"epss": EPSS_URL, "kev": KEV_REPO_URL},
        "items": items,
    }


def build_intel_index(threat_intel: Any) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    if not isinstance(threat_intel, dict):
        return idx
    for item in as_list(threat_intel.get("items")):
        if not isinstance(item, dict):
            continue
        cve = norm_cve(item.get("cve"))
        if not cve:
            continue
        idx[cve] = {
            "cisa_kev_listed": bool(item.get("cisa_kev_listed", False)),
            "epss_probability": item.get("epss_probability"),
            "epss_percentile": item.get("epss_percentile"),
            "kev_date_added": item.get("kev_date_added"),
            "kev_due_date": item.get("kev_due_date"),
        }
    return idx


def req_metric(value: Any, prefix: str) -> str:
    if not isinstance(value, str):
        return f"{prefix}:X"
    v = value.strip().lower()
    if v == "high":
        return f"{prefix}:H"
    if v == "medium":
        return f"{prefix}:M"
    if v == "low":
        return f"{prefix}:L"
    return f"{prefix}:X"


def env_metrics(context: Any) -> Dict[str, str]:
    if not isinstance(context, dict):
        return {
            "CR": "CR:X",
            "IR": "IR:X",
            "AR": "AR:X",
            "MAV": "MAV:X",
            "MPR": "MPR:X",
            "MAC": "MAC:X",
            "exposure": "unknown",
            "runtime_presence_default": "unknown",
        }

    cr = req_metric(context.get("confidentiality_requirement"), "CR")
    ir = req_metric(context.get("integrity_requirement"), "IR")
    ar = req_metric(context.get("availability_requirement"), "AR")

    ingress = context.get("ingress") if isinstance(context.get("ingress"), dict) else {}
    reach = (
        context.get("network_reachability")
        if isinstance(context.get("network_reachability"), dict)
        else {}
    )

    if (
        ingress.get("public_lb") is True
        or ingress.get("public_ip") is True
        or ingress.get("sg_allows_0_0_0_0") is True
        or reach.get("reachable_from_internet") is True
    ):
        mav = "MAV:N"
    elif reach.get("reachable_from_same_vpc") is True:
        mav = "MAV:A"
    elif reach.get("reachable_only_from_same_host") is True:
        mav = "MAV:L"
    else:
        mav = "MAV:X"

    mpr_map = {
        "none": "MPR:N",
        "user": "MPR:L",
        "service": "MPR:L",
        "admin": "MPR:H",
    }
    pr = context.get("privileges_required")
    mpr = mpr_map.get(pr.strip().lower(), "MPR:X") if isinstance(pr, str) else "MPR:X"

    exposure = context.get("exposure") if isinstance(context.get("exposure"), str) else "unknown"
    exposure = exposure.strip().lower()
    auth_boundary = (
        context.get("auth_boundary").strip().lower()
        if isinstance(context.get("auth_boundary"), str)
        else "unknown"
    )

    if context.get("requires_mtls") is True or context.get("service_mesh_policy_enforced") is True:
        mac = "MAC:H"
    elif exposure == "internal" and auth_boundary != "none":
        mac = "MAC:H"
    elif exposure == "public" and auth_boundary == "none":
        mac = "MAC:L"
    else:
        mac = "MAC:X"

    runtime_default = "unknown"
    rp = context.get("runtime_presence")
    if isinstance(rp, str) and rp.strip().lower() in RUNTIME_RANK:
        runtime_default = rp.strip().lower()

    return {
        "CR": cr,
        "IR": ir,
        "AR": ar,
        "MAV": mav,
        "MPR": mpr,
        "MAC": mac,
        "exposure": exposure,
        "runtime_presence_default": runtime_default,
    }


def env_overrides_payload(context: Any) -> Dict[str, Any]:
    env = env_metrics(context)
    runtime_by_package = {}
    if isinstance(context, dict) and isinstance(context.get("runtime_presence_by_package"), dict):
        for pkg, val in context["runtime_presence_by_package"].items():
            if isinstance(pkg, str) and isinstance(val, str):
                norm_val = val.strip().lower()
                if norm_val in RUNTIME_RANK:
                    runtime_by_package[pkg.strip().lower()] = norm_val

    rationale = {
        "CR": "Mapped from confidentiality_requirement in context.json",
        "IR": "Mapped from integrity_requirement in context.json",
        "AR": "Mapped from availability_requirement in context.json",
        "MAV": "Mapped from ingress/network_reachability booleans",
        "MAC": "Mapped from mTLS/mesh policy and exposure+auth boundary",
        "MPR": "Mapped from privileges_required",
    }

    return {
        "generated_at": utc_now_iso(),
        "source": "context.json",
        "overrides": {
            "CR": env["CR"],
            "IR": env["IR"],
            "AR": env["AR"],
            "MAV": env["MAV"],
            "MAC": env["MAC"],
            "MPR": env["MPR"],
            "exposure": env["exposure"],
        },
        "runtime_presence_default": env["runtime_presence_default"],
        "runtime_presence_by_package": runtime_by_package,
        "rationale": rationale,
    }


def threat_metric(intel: Dict[str, Any]) -> str:
    if intel.get("cisa_kev_listed") is True:
        return "A"
    epss = intel.get("epss_probability")
    if isinstance(epss, (int, float)):
        if epss >= 0.90:
            return "A"
        if epss >= 0.70:
            return "F"
        if epss >= 0.30:
            return "P"
        return "U"
    return "X"


def runtime_presence(env_overrides: Any, package: str) -> str:
    if not isinstance(env_overrides, dict):
        return "unknown"

    by_pkg = env_overrides.get("runtime_presence_by_package")
    if isinstance(by_pkg, dict):
        v = by_pkg.get(package)
        if isinstance(v, str):
            n = v.strip().lower()
            if n in RUNTIME_RANK:
                return n

    v = env_overrides.get("runtime_presence_default")
    if isinstance(v, str):
        n = v.strip().lower()
        if n in RUNTIME_RANK:
            return n
    return "unknown"


def exposure_sub(mav: str) -> float:
    return {
        "MAV:N": 1.00,
        "MAV:A": 0.60,
        "MAV:L": 0.30,
        "MAV:X": 0.50,
    }.get(mav, 0.50)


def impact_sub(cr: str, ir: str, ar: str) -> float:
    vals = {cr, ir, ar}
    if "CR:H" in vals or "IR:H" in vals or "AR:H" in vals:
        return 1.00
    if "CR:M" in vals or "IR:M" in vals or "AR:M" in vals:
        return 0.70
    if vals.issubset({"CR:L", "IR:L", "AR:L"}):
        return 0.40
    return 0.50


def final_vector(base_vector: Optional[str], e: str, env: Dict[str, str]) -> Optional[str]:
    if not base_vector:
        return None
    parts = [base_vector, f"E:{e}"]
    for key in ("CR", "IR", "AR", "MAV", "MAC", "MPR"):
        val = env[key]
        if not val.endswith(":X"):
            parts.append(val)
    return "/".join(parts)


def recommended_action(package: str, fix_version: Optional[str], source_bucket: str) -> str:
    if package != "unknown" and fix_version:
        return f"Upgrade {package} to {fix_version}"
    if package != "unknown" and source_bucket != "ECR-only":
        return f"Upgrade {package}; fixed version unknown in input"
    if source_bucket == "ECR-only" and not fix_version:
        return "Update base image and rebuild"
    if source_bucket == "ECR-only" and fix_version:
        return "Rebuild image to pick up upstream patches"
    return "Investigate; insufficient data in inputs"


def fmt_sub(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def bool_yn(v: bool) -> str:
    return "yes" if v else "no"


def markdown_escape(value: Any) -> str:
    s = "" if value is None else str(value)
    return s.replace("|", "\\|")
