"""
Copyright (c) 2023 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import datetime
import time
import csv
import meraki
import config


# Firmware upgrades endpoint: https://developer.cisco.com/meraki/api-v1/#!get-network-firmware-upgrades
# Action batches: https://developer.cisco.com/meraki/api-v1/#!action-batches-overview


# Initialize the Meraki API session
dashboard = meraki.DashboardAPI(api_key=config.api_key, suppress_logging=True, single_request_timeout=120)

# Configuration options
organization_id = config.organization_id
time_delta_in_days =config.time_delta_in_days
actions_per_batch = 100
wait_factor = 0.33

# Function to format time for API requirements
def time_formatter(date_time_stamp):
    formatted_date_time_stamp = date_time_stamp.replace(microsecond=0).isoformat() + 'Z'
    return formatted_date_time_stamp

# Calculate current and future timestamps
utc_now = datetime.datetime.utcnow()
utc_future = utc_now + datetime.timedelta(days=time_delta_in_days)
utc_now_formatted = time_formatter(utc_now)
utc_future_formatted = time_formatter(utc_future)

# Define the action for rescheduling firmware upgrades
product_type = 'temp'
action_reschedule_existing = {
    "products": {
        f"{product_type}": {
            "nextUpgrade": {
                "time": utc_future_formatted
            }
        }
    }
}

# Fetch the list of networks from Meraki
networks_list = dashboard.organizations.getOrganizationNetworks(organizationId=organization_id)

# Create a dictionary to map network IDs to their names for easy lookup
network_id_to_name = {network['id']: network['name'] for network in networks_list}

# Function to format a single action for the Meraki API
def format_single_action(resource, operation, body):
    action = {
        "resource": resource,
        "operation": operation,
        "body": body
    }
    return action

# Function to create a single upgrade action for a given network and product
def create_single_upgrade_action(network_id, products):
    actions = []
    for product in products:
        action_resource = f'/networks/{network_id}/firmwareUpgrades'
        action_operation = 'update'
        action_body = {
            "products": {
                product: {
                    "nextUpgrade": {
                        "time": utc_future_formatted
                    }
                }
            }
        }
        action = format_single_action(action_resource, action_operation, action_body)
        actions.append(action)
    return actions

# Function to run an action batch
def run_an_action_batch(org_id, actions_list, synchronous=False):
    batch_response = dashboard.organizations.createOrganizationActionBatch(
        organizationId=org_id,
        actions=actions_list,
        confirmed=True,
        synchronous=synchronous
    )
    return batch_response

# Function to split actions into batches of a specified size
def batch_actions_splitter(batch_actions):
    for i in range(0, len(batch_actions), actions_per_batch):
        yield batch_actions[i:i + actions_per_batch]

# Function to run multiple action batches and log results to a CSV
def action_batch_runner(batch_actions_lists, org_id):
    responses = list()
    number_of_batches = len(batch_actions_lists)
    number_of_batches_submitted = 0

    with open('upgraded_networks_log.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Network Name', 'Product', 'New Upgrade Time'])

        for batch_action_list in batch_actions_lists:
            action_batch_queue_checker(org_id)
            batch_response = run_an_action_batch(org_id, batch_action_list)
            responses.append(batch_response)
            number_of_batches_submitted += 1

            for action in batch_action_list:
                network_id = action['resource'].split('/')[-2]
                network_name = network_id_to_name[network_id]
                product = list(action['body']['products'].keys())[0]
                upgrade_time = action['body']['products'][product]['nextUpgrade']['time']
                csvwriter.writerow([network_name, product, upgrade_time])

    return responses

# Function to check the queue of action batches and wait if necessary
def action_batch_queue_checker(org_id):
    all_action_batches = dashboard.organizations.getOrganizationActionBatches(organizationId=org_id)
    running_action_batches = [batch for batch in all_action_batches if
                              batch['status']['completed'] is False and batch['status']['failed'] is False]
    total_running_actions = 0

    for batch in running_action_batches:
        batch_actions = len(batch['actions'])
        total_running_actions += batch_actions

    wait_seconds = total_running_actions * wait_factor

    while len(running_action_batches) > 4:
        time.sleep(wait_seconds)
        all_action_batches = dashboard.organizations.getOrganizationActionBatches(organizationId=org_id)
        running_action_batches = [batch for batch in all_action_batches if
                                  batch['status']['completed'] is False and batch['status']['failed'] is False]
        total_running_actions = 0

        for batch in running_action_batches:
            batch_actions = len(batch['actions'])
            total_running_actions += batch_actions

        wait_seconds = total_running_actions * wait_factor
    return all_action_batches

# Function to determine which products in a network need to be upgraded soon
def products_to_upgrade_soon(network):
    firmware_upgrades = dashboard.networks.getNetworkFirmwareUpgrades(networkId=network['id'])
    products_to_upgrade = []
    for product in network['productTypes']:
        if product in firmware_upgrades['products'] and 'nextUpgrade' in firmware_upgrades['products'][product]:
            upgrade_time = firmware_upgrades['products'][product]['nextUpgrade'].get('time', None)
            if upgrade_time:
                upgrade_datetime = datetime.datetime.strptime(upgrade_time, '%Y-%m-%dT%H:%M:%SZ')
                if 0 <= (upgrade_datetime - utc_now).days < config.days_before_upgrade:
                    products_to_upgrade.append(product)
    return products_to_upgrade

# Determine which networks need firmware upgrades
networks_products_to_upgrade = {network['id']: products_to_upgrade_soon(network) for network in networks_list if products_to_upgrade_soon(network)}

# Create a list of upgrade actions based on the networks and products that need upgrades
upgrade_actions_list = []
for network_id, products in networks_products_to_upgrade.items():
    upgrade_actions_list.extend(create_single_upgrade_action(network_id, products))

# Split the upgrade actions into batches
upgrade_actions_lists = list(batch_actions_splitter(upgrade_actions_list))

# Run the action batches
upgraded_networks_responses = action_batch_runner(upgrade_actions_lists, organization_id)

print("All action batches submitted!")
print(action_batch_queue_checker(organization_id))
print("Script completed successfully!")
