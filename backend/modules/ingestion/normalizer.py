"""
modules/ingestion/normalizer.py - Chuan hoa alert tu Alertmanager
Chuyen payload goc thanh format thong nhat cua he thong
"""
import hashlib
import json


def normalize_alertmanager(payload: dict) -> list[dict]:
    """
    Nhan payload tu Alertmanager webhook, tra ve list incidents da chuan hoa.

    Alertmanager gui 1 payload co the chua NHIEU alerts.
    Moi alert se duoc chuan hoa thanh 1 normalized event.
    """
    alerts = payload.get("alerts", [])
    results = []

    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        # Tao fingerprint de dedup (khong tao trung)
        # fingerprint = hash cua alertname + sorted labels
        fp_data = labels.get("alertname", "") + json.dumps(labels, sort_keys=True)
        fingerprint = hashlib.sha256(fp_data.encode()).hexdigest()[:16]

        # Map severity
        severity = labels.get("severity", "medium")
        if severity not in ("critical", "high", "medium", "low", "info"):
            severity = "medium"

        # Trich xuat host tu instance label
        instance = labels.get("instance", "")
        host = instance.split(":")[0] if instance else labels.get("host", "")

        normalized = {
            "title": f"[{labels.get('alertname', 'Unknown')}] {annotations.get('summary', '')}",
            "severity": severity,
            "source": "alertmanager",
            "fingerprint": fingerprint,
            "impacted_service": labels.get("service", labels.get("job", "")),
            "impacted_host": host,
            "status_from_alert": alert.get("status", "firing"),  # firing/resolved
            "normalized_event": {
                "alertname": labels.get("alertname"),
                "severity": severity,
                "instance": instance,
                "host": host,
                "service": labels.get("service", labels.get("job", "")),
                "summary": annotations.get("summary", ""),
                "description": annotations.get("description", ""),
                "starts_at": alert.get("startsAt"),
                "ends_at": alert.get("endsAt"),
                "generator_url": alert.get("generatorURL", ""),
                "labels": labels,
                "annotations": annotations,
            },
            "raw_alert": alert,
        }
        results.append(normalized)

    return results
