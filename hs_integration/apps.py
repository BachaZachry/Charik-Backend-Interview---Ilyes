from django.apps import AppConfig
from hubspot import HubSpot

from config.settings import HUBSPOT_API_KEY


class HsIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hs_integration"

    # Load API on app start
    api_client = HubSpot(access_token=HUBSPOT_API_KEY)
    contacts_api = api_client.crm.contacts.basic_api
    deals_api = api_client.crm.deals.basic_api
    association_api = api_client.crm.associations.batch_api
