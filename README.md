# gve_devnet_meraki_firmware_upgrade_deadline_extender

This prototype script scans the upcoming firmware upgrade deadlines for all Meraki product types. If the deadline is within a specified threshold of days, the script will extend the upgrade deadline by a predetermined number of days, ensuring devices remain updated without unexpected disruptions.

## Contacts
* Jorge Banegas

## Solution Components
* Meraki
* Project expanded from this [repo](https://github.com/meraki/dashboard-api-python/blob/main/examples/bulk_firmware_upgrade_manager.py)

## Prerequisites

#### Meraki API Keys
To use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions:
1. Login to the Meraki dashboard.
2. Navigate to `Organization > Settings > Dashboard API access`.
3. Click on `Enable access to the Cisco Meraki Dashboard API`.
4. Go to `My Profile > API access`.
5. Click on `Generate API key`.
6. Save the API key in a safe place. The API key will only be shown once for security purposes.

> For more information on generating an API key, click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization).

> Note: Add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).

#### Meraki Organization ID
Visit https://developer.cisco.com/meraki/api/get-organizations/ to retrieve the ID number for your organization. 

1. Enter your Meraki API key after Bearer. Ex. Bearer xxxxxxxxxxxxxxxxx
2. Look for your organization and save the ID 


## Installation/Configuration
1. Clone this repository with `git clone [repository name]`.
2. Add Meraki API key to environment variables:
```python
api_key='YOUR_API_KEY_HERE'
organization_id = 'YOUR_ORGANIZATION_ID'  
days_before_upgrade = 7
time_delta_in_days = 14
```
3. Set up a Python virtual environment. Ensure Python 3 is installed. If not, download Python [here](https://www.python.org/downloads/). Activate the virtual environment with the instructions [here](https://docs.python.org/3/tutorial/venv.html).
4. Install the requirements with `pip3 install -r requirements.txt`.

## Usage
To run the program, use the command:
```
$ python3 main.py
```

# Screenshots
Log file to display which networks and products had their firmware schedule delayed 

![/IMAGES/0image.png](/IMAGES/output.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is for demo purposes only. All tools/scripts in this repo are "AS IS" without any warranties. Use these scripts and tools at your own risk. We don't guarantee they have been through thorough testing in a comparable environment and we aren't responsible for any damage or data loss incurred with their use. Review and test any scripts thoroughly before use in a non-testing environment.
