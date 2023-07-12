1. Create a Google Cloud Console project at console.cloud.google.com
    1. Create Cloud Console oAuth 2.0 credentials
    2. Set a redirect URI
    3. Turn on the Smart Device Access API
2. Create a Device Access project at console.nest.google.com

VALUES NEEDED:
From https://console.cloud.google.com/apis/credentials:
    OAuth Client ID
    OAuth Client Secret
    (Google Cloud Project ID is not the Project ID you are looking for)

From https://console.nest.google.com/device-access/project-list:
    Device Access Project ID

3. Assemble a login URL and visit it to log in and authorize access
    https://nestservices.google.com/partnerconnections/<project_id>/auth
        ?redirect_uri=<redirect_uri>
        &access_type=offline
        &prompt=consent
        &client_id=<client_id>
        &response_type=code
        &scope=https://www.googleapis.com/auth/sdm.service

4. In the redirect URL, grab the value of 'code' (should look like '4/...')

5. POST to 'https://www.googleapis.com/oauth2/v4/token' to get an access token (valid for 60m) and refresh token
    a. Initial request
        params:
            'client_id'     , '<client_id>'    
            'client_secret' , '<client_secret>'
            'code'          , '<code>'         
            'grant_type'    , 'authorization_code'   
            'redirect_uri'  , '<redirect_uri>' 
        response:
            'token_type'
            'access_token'
            'refresh_token'

    b. Subsequent request
        params:
            'client_id'     , '<client_id>'
            'client_secret' , '<client_secret>'
            'refresh_token' , '<refresh_token>'
            'grant_type'    , 'refresh_token'
        
