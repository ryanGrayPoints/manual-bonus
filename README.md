# manual-bonus
Requires all 4 files in repository to execute

Also requires the requests library, to install run $ python -m pip install requests

Update lcp_credentials.py with the appropriate credentials

CSV file needs 2 headers "parent_order" and "offer", the values for each should be self explanatory

CSV file should be in same directory as .py files

Add the CSV file name to file_name property in emirates.py

Add the correct Jira ticket ID to ticket_id property also in emirates.py

When script is done running, a CSV file will be created with the following headers: ticket, offer, parent_order, order_url, parent_order_amount, bonus_amount, credit_status, order_status, pts_app_cid

Every record, regardless of status, will be included in its own row withint the CSV file

Every request executed as part of the same manual bonus order will have a single unique Pts-App-CID for easy Splunking

All Pts-App-CID's will end with "Emirates Manual Bonus"





