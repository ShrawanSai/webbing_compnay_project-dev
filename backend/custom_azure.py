from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'djangostoragewc' # Must be replaced by your <storage_account_name>
    account_key = 'aJxkDop8hX95ip+h4ETS2Isxf/jbMdbxM726poup/y//JV7b13qwiHj2x5aqbKR/o6TLAdqOY/fG+AStC5Np4Q==' # Must be replaced by your <storage_account_key>
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'djangostoragewc' # Must be replaced by your storage_account_name
    account_key = 'aJxkDop8hX95ip+h4ETS2Isxf/jbMdbxM726poup/y//JV7b13qwiHj2x5aqbKR/o6TLAdqOY/fG+AStC5Np4Q==' # Must be replaced by your <storage_account_key>
    azure_container = 'static'
    expiration_secs = None