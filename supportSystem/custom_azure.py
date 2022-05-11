import os

from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = os.getenv("AZURE_STORAGE_NAME")
    account_key = os.getenv("AZURE_STORAGE_MEDIA_KEY")
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = os.getenv("AZURE_STORAGE_NAME")
    account_key = os.getenv("AZURE_STORAGE_STATIC_KEY")
    azure_container = 'static'
    expiration_secs = None