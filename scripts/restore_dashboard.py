#!/usr/bin/env python3
import os
import json
import requests
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


def import_dashboard(export_file, token):
    """Import dashboard from export file"""
    headers = {"Authorization": f"Bearer {token}"}

    import_url = f"{os.environ['SUPERSET_URL']}/api/v1/dashboard/import/"

    with open(export_file, 'rb') as f:
        files = {'formData': ('export.zip', f, 'application/zip')}
        data = {'overwrite': 'true'}

        response = requests.post(import_url, files=files, data=data, headers=headers)
        response.raise_for_status()

    return response.json()


def main():
    dashboard_id = os.environ.get('DASHBOARD_ID')

    if not dashboard_id:
        print("DASHBOARD_ID environment variable required")
        return

    # Find dashboard export file
    dashboard_dir = Path(f"dashboards/{dashboard_id}")
    export_file = dashboard_dir / "export.zip"

    if not export_file.exists():
        print(f"Export file not found: {export_file}")
        return

    # Get Superset token
    token = get_superset_token()

    # Import dashboard
    result = import_dashboard(export_file, token)

    print(f"Dashboard {dashboard_id} restored successfully")
    print(f"Import result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()