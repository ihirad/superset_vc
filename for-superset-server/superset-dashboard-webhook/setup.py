from setuptools import setup, find_packages

setup(
    name="superset-dashboard-webhook",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "apache-superset",
        "requests"
    ],
    entry_points={
        'superset.extensions': [
            'dashboard_webhook = superset_dashboard_webhook.plugin:DashboardWebhookPlugin'
        ]
    }
)
