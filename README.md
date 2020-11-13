# Cisco & Meraki License status
Script to obtain the Cisco and Meraki license status and it´s details

### Usage
Clone the scripts, add the environmental variables and you are ready to go. Modify, in the main function the list of recipients (send_to) and you´ll be
 ready to go! They will receive an email with license details

### Environmental Variables
For security purposes all variables containing passwords and or compromising information is stored in an environmental variable. Here´s a brief explanation
 of what each should be filled with
 
* MERAKI_ULR: Meraki's Api base url (up to version)
* ENDPOINT_ORGANIZATION: Meraki's organization endpoint without the base url (whatever it's after version)
* ENDPOINT_LICENSE: Meraki's license endpoint without the base url (whatever it's after version)
* MERAKI_API_KEY: Meraki's access key
* URL_TOKEN: Cisco's url to generate client's token
* URL_VIRTUAL_ACCOUNTS: Cisco's url to get the Account Domain's virtual accounts
* URL_LICENSES: Cisco Smart License Usage url
* CISCO_TOKEN_PAYLOAD: Oath2 details (in client_id=xxx&client_secret=xxx&grant_type=xxx&username=xxx&password=xxx fashion) 
* EXCEPTION_NAME: If for some reason there's an empty or problematic organization name in Meraki's platform add it here
* EMAIL_USER: email's account username address from where the results will be sent 
* EMAIL_PASS: email's account password
* EMAIL_SERVER: email's account SMTP server (for example, smtp.gmail.com)

### Useful links

#### For Cisco
* https://anypoint.mulesoft.com/apiplatform/apx/#/portals/organizations/1c92147b-332d-4f44-8c0e-ad3997b5e06d/apis/5418104/versions/102456/pages/309243
* https://anypoint.mulesoft.com/apiplatform/apx#/portals/organizations/1c92147b-332d-4f44-8c0e-ad3997b5e06d/apis/5418104/versions/102456/pages/425744

#### For Meraki
* https://developer.cisco.com/meraki/
* https://developer.cisco.com/meraki/api-v1/
