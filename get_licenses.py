#!/usr/bin/python

__author__ = "Beltran Esteva"

import requests
import logging
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from requests.exceptions import Timeout
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from os import environ
from dotenv import load_dotenv
from error import error_handler

# loading environmental variables
load_dotenv(".env", verbose=True)

LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(filename) -25s %(lineno) -5d]: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%d/%m/%Y %H:%M:%S') #, filename='logs.txt')

# environmental variables
MERAKI_URL = environ.get('MERAKI_URL')
MERAKI_API_KEY = environ.get('MERAKI_API_KEY')
HEADERS_MERAKI = {'X-Cisco-Meraki-API-Key': MERAKI_API_KEY}
HEADERS_CISCO_TOKEN = {'Content-Type': 'application/x-www-form-urlencoded'}
HEADERS_CISCO = {'ContentType': 'application/json'}
CISCO_TOKEN_PAYLOAD = environ.get('CISCO_TOKEN_PAYLOAD')
ENDPOINT_ORGANIZATION = environ.get('ENDPOINT_ORGANIZATION')
ENDPOINT_LICENSE = environ.get('ENDPOINT_LICENSE')
URL_TOKEN = environ.get('URL_TOKEN')
URL_VIRTUAL_ACCOUNTS = environ.get('URL_VIRTUAL_ACCOUNTS')
URL_LICENSES = environ.get('URL_LICENSES')
EXCEPTION_NAME = environ.get('EXCEPTION_NAME')

# email variables
EMAIL_USER = environ.get('EMAIL_USER')
EMAIL_PASS = environ.get('EMAIL_PASS')
EMAIL_SERVER = environ.get('EMAIL_SERVER')

# Retry strategy
retry_strategy = Retry(
    total=5,
    status_forcelist=[408, 429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# allow self signed certs
requests.packages.urllib3.disable_warnings()

MERAKI_HTML_TABLE = """
        <table width="90%" style="border-collapse: collapse; border:1px solid black">
            <thead>
                <tr style="border:1px solid black">
                    <th colspan="3" style="border:1px solid black; background-color: grey">{}</th>
                </tr>
                <tr>
                  <th style="border:1px solid black">Organization</th>
                  <th style="border:1px solid black">Status</th>
                  <th style="border:1px solid black">Expiration Date</th>
                </tr>
            </thead>
            <tbody style="text-align:center; border:1px solid black">
                {}
            </tbody>
        </table><br><br>"""

CISCO_HTML_TABLE = """
        <table width="90%" style="border-collapse: collapse; border:1px solid black">
            <thead>
                <tr style="border:1px solid black">
                    <th colspan="9" style="border:1px solid black; background-color: grey">{}</th>
                </tr>
                <tr>
                  <th style="border:1px solid black" rowspan="2">Virtual Account</th>
                  <th style="border:1px solid black" rowspan="2">Status</th>
                  <th style="border:1px solid black" rowspan="2">License</th>
                  <th style="border:1px solid black" colspan="6">License Details</th>
                </tr>
                <tr>
                  <th style="border:1px solid black">License Type</th>
                  <th style="border:1px solid black">Quantity</th>
                  <th style="border:1px solid black">End Date</th>
                  <th style="border:1px solid black">Subscription Id</th>
                  <th style="border:1px solid black">Start Date</th>
                  <th style="border:1px solid black">Status</th>
                </tr>
            </thead>
            <tbody style="text-align:center; border:1px solid black">
                {}
            </tbody>
        </table><br><br>"""


class Email:
    """Returns a boolean indicating if email was sent or not

    Sends and email based on
    """
    send_from = EMAIL_USER
    server = EMAIL_SERVER
    password = EMAIL_PASS

    def __init__(self, send_to, subject, body):
        self.send_to = send_to
        self.subject = subject
        self.body = body
        self.sendmail()

    def sendmail(self):
        # preparing the email to be sent
        msg = MIMEMultipart()
        msg['From'] = Email.send_from
        msg['To'] = COMMASPACE.join(self.send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = str(self.subject)
        html_body = MIMEText(self.body, 'html')

        msg.attach(html_body)
        try:
            with smtplib.SMTP(host=Email.server, port=587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(Email.send_from, Email.password)
                smtp.sendmail(Email.send_from, self.send_to, msg.as_string())
            return True

        except Exception:
            return False


class Meraki:
    """Return an html table with the different organizations and it´s license status.

    Create an html table that maps the different organizations handled in Meraki's platform and the license status, devices and expirations date.

    Return:
        An html table mapping each organization with it's license status and expiration date
        For example:

        Organization | Status | Expiration Date
    """
    url_organization = ''.join([MERAKI_URL, ENDPOINT_ORGANIZATION])
    headers = HEADERS_MERAKI

    def __init__(self):
        self.organizations = []
        self.license_status = {}
        self.get_organization()
        self.get_license()

    @error_handler
    def get_organization(self):
        response = http.get(url=Meraki.url_organization, verify=False, headers=HEADERS_MERAKI, timeout=10)
        self.organizations = [{'name': organization['name'], 'id':organization['id']} for organization in response.json()
                              if organization['name'] != EXCEPTION_NAME]

        return self.organizations

    @error_handler
    def get_license(self):
        for item in self.organizations:
            url_license = ''.join([MERAKI_URL, ENDPOINT_LICENSE.format(item['id'])])
            response = http.get(url=url_license, verify=False, headers=Meraki.headers, timeout=10)
            self.license_status[item['name']] = response.json()

        return self.license_status

    def show(self):
        html_skeleton = MERAKI_HTML_TABLE
        row_skeleton = '<tr>{}</tr>'
        simple_cell_skeleton = '<td style="border:1px solid black">{}</td>'
        column = []
        for item in self.license_status:
            cell = [simple_cell_skeleton.format(item), simple_cell_skeleton.format(self.license_status[item]['status']),
                    simple_cell_skeleton.format(self.license_status[item]['expirationDate']), '</tr><tr>']
            joint_cells = ''.join(cell)
            column.append(joint_cells)

        joint_columns = ''.join(column)
        html = html_skeleton.format('Meraki', row_skeleton.format(joint_columns))

        return html


class Cisco:
    """Return an html table with the different virtual accounts and it´s license status.

        Create an html table that maps the different organizations handled in Cisco's platform and the license status, devices and expirations date.

        Return:
            An html table mapping each virtual account with it's license status and expiration date
            For example:

            VirtualAccount | Status | License | License Type | Quantity	 | End Date	 | Subscription Id | Start Date | Status
    """
    url_token = URL_TOKEN
    url_virtual_accounts = URL_VIRTUAL_ACCOUNTS
    url_licenses = URL_LICENSES
    headers_token = HEADERS_CISCO_TOKEN
    headers = HEADERS_CISCO
    get_token_payload = CISCO_TOKEN_PAYLOAD

    def __init__(self):
        self._token = self.get_token()
        self.authorization = ''
        self.headers = {'Authorization': self.authorization}
        self.virtual_accounts = self.get_virtual_account()
        self.licenses = self.get_license()

    @error_handler
    def get_token(self):
        response = http.post(url=Cisco.url_token, headers=Cisco.headers_token, data=Cisco.get_token_payload, verify=False, timeout=10)
        # print(response.text)

        return response.json()['access_token']

    @error_handler
    def get_virtual_account(self):
        self.authorization = ' '.join(['Bearer', self._token])
        headers = {'Authorization': self.authorization}
        response = http.get(url=Cisco.url_virtual_accounts, headers=headers, verify=False, timeout=10)
        virtual_accounts = [account['name'] for account in response.json()['virtualAccounts']]
        # print(virtual_accounts)

        return virtual_accounts

    @error_handler
    def get_license(self):
        header = {'Authorization': self.authorization, 'Content-Type': 'application/json'}
        payload = {"virtualAccounts": self.virtual_accounts, "limit": 200, "offset": 0}
        response = http.post(url=Cisco.url_licenses, headers=header, data=json.dumps(payload), verify=False, timeout=10)
        # print(f'licenses: {json.dumps(response.json(), indent=2)}')
        return response.json()

    def show(self):
        html_skeleton = CISCO_HTML_TABLE
        row_skeleton = '<tr>{}</tr>'
        multi_cell_skeleton = '<td style="border:1px solid black" rowspan="{}">{}</td>'
        simple_cell_skeleton = '<td style="border:1px solid black">{}</td>'
        column = []
        for item in self.licenses['licenses']:

            if item['quantity']:
                row_num = len(item['licenseDetails'])
                cell = [multi_cell_skeleton.format(row_num, item['virtualAccount']), multi_cell_skeleton.format(row_num, item['status']),
                        multi_cell_skeleton.format(row_num, item['license'])]
                for i in item['licenseDetails']:
                    cell.append(simple_cell_skeleton.format(i['licenseType']))
                    cell.append((simple_cell_skeleton.format(i['quantity'])))
                    cell.append((simple_cell_skeleton.format(i['endDate'])))
                    cell.append((simple_cell_skeleton.format(i['subscriptionId'])))
                    cell.append((simple_cell_skeleton.format(i['startDate'])))
                    cell.append((simple_cell_skeleton.format(i['status'])))
                    cell.append('</tr><tr>')
            else:
                row_num = 1
                cell = [multi_cell_skeleton.format(row_num, item['virtualAccount']), multi_cell_skeleton.format(row_num, item['status']),
                        multi_cell_skeleton.format(row_num, item['license']), '<td style="border:1px solid black" colspan="6"></td></tr><tr>']

            joint_cells = ''.join(cell)
            column.append(joint_cells)

        joint_columns = ''.join(column)
        html = html_skeleton.format('Cisco', row_skeleton.format(joint_columns))

        return html


def get_licenses():
    # obtaining license details in html format
    html_meraki = Meraki().show()
    html_viptela = Cisco().show()

    # adding email separators and headlines for both tables
    head_meraki = 'Meraki license details:<br><br>'
    head_cisco = 'Cisco license details:<br><br>'

    # finalizing the html
    message = ''.join([head_meraki, html_meraki, head_cisco, html_viptela])

    # defining recipients
    send_to = ['xxx@xxx']

    # sending email
    Email(send_to, 'SD-WAN license status', message)

    print('email sent')


if __name__ == '__main__':
    get_licenses()
