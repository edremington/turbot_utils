import requests
from urllib.parse import urljoin

def version(turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification, turbot_host, turbot_account_urn):
    """ Gets the turbot version
    :returns: Returns a string turbot_version"""
    
    api_method = "GET"
    api_url = "/api/v1/resources/%s/options" % (turbot_account_urn)
    #api_url = "/api/v1/resources/urn:turbot:{clusterId}:{accountId}/options"
        
      
    response = requests.request(
        api_method,
        urljoin(turbot_host, api_url),
        auth=(turbot_api_access_key, turbot_api_secret_key),
        verify=turbot_host_certificate_verification,
        headers={
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
    )

    print('Turbot version=%s' % response.headers['X-Turbot-Version'])
    return response.headers['X-Turbot-Version']

#if __name__ == '__main__':
 #   import turbotutils
  #  import turbotutils.cluster
   # turbot_host_certificate_verification = True

    # Set to your Turbot Host URL
    #turbot_host = turbotutils.get_turbot_host()
    # Get the access and secret key pairs
    #(turbot_api_access_key, turbot_api_secret_key) = turbotutils.get_turbot_access_keys()
    #urn_format = turbotutils.cluster.get_cluster_id(turbot_host, turbot_api_access_key, turbot_api_secret_key, turbot_host_certificate_verification)
    
    #get_turbot_version ( turbot_api_access_key, turbot_api_secret_key,turbot_host_certificate_verification,turbot_host,urn_format )