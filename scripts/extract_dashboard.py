#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from pathlib import Path


def get_superset_token():
    """Authenticate with Superset and get access token"""
    login_url = f"{os.environ['SUPERSET_URL']}/api/v1/security/login"

    payload = {
        "username": os.environ['SUPERSET_USERNAME'],
        "password": os.environ['SUPERSET_PASSWORD'],
        "provider": "db",
        "refresh": True
    }

    response = requests.post(login_url, json=payload)
    response.raise_for_status()

    return response.json()["access_token"]


def export_dashboard(dashboard_id, token):
    """Export dashboard configuration"""
    headers = {"Authorization": f"Bearer {token}"}

    # Export dashboard
    export_url = f"{os.environ['SUPERSET_URL']}/api/v1/dashboard/export/"
    payload = {"dashboard_ids": [dashboard_id]}

    response = requests.post(export_url, json=payload, headers=headers)
    response.raise_for_status()

    return response.content


def main():
    # Get dashboard data from webhook
    dashboard_data = json.loads(os.environ.get('DASHBOARD_DATA', '{}'))

    if not dashboard_data:
        print("No dashboard data provided")
        return

    dashboard_id = dashboard_data['id']
    dashboard_title = dashboard_data['dashboard_title']

    # Get Superset token
    token = get_superset_token()

    # Export dashboard
    export_content = export_dashboard(dashboard_id, token)

    # Create directory structure
    dashboard_dir = Path(f"dashboards/{dashboard_id}")
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    # Save export file
    export_file = dashboard_dir / "export.zip"
    with open(export_file, 'wb') as f:
        f.write(export_content)

    # Save metadata
    metadata = {
        "dashboard_id": dashboard_id,
        "dashboard_title": dashboard_title,
        "exported_at": datetime.utcnow().isoformat(),
        "superset_url": os.environ['SUPERSET_URL'],
        "webhook_data": dashboard_data
    }

    metadata_file = dashboard_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Dashboard {dashboard_id} exported successfully")


if __name__ == "__main__":
    main()