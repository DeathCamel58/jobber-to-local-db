import math

from configparser import ConfigParser

import requests
import json

# Console UI stuff
from rich import print
from rich.pretty import pprint
from rich.progress import track

configuration_file = ConfigParser()
configuration_file.read('config.ini')

cookies = {
    '_jobber_session_id': configuration_file.get('jobber', 'jobber_session_id'),
    'j_identity_token': configuration_file.get('jobber', 'j_identity_token'),
    'redirect_url': 'https://secure.getjobber.com/today',
    'state': '300'
}

out_location = 'data/'


def write_data(file_name, data):
    with open(f'{out_location}/{file_name}.json', 'w') as file:
        file.write(json.dumps(data))


def get_clients():
    print("Getting Clients")
    r = requests.get("https://secure.getjobber.com/reports/clients.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_clients = json.loads(r.content)["iTotalRecords"]
    print(f'{num_clients} invoices found!')

    # Iterate over all clients, 250 at once
    all_clients = []
    for i in track(range(math.ceil(num_clients/250)), description="Getting Client Data..."):
        r = requests.get("https://secure.getjobber.com/reports/clients.json", cookies=cookies, params={
            'iDisplayStart': (i*250)+1,
            'iDisplayLength': 250
        })

        json_data = json.loads(r.content)
        clients = json_data['aaData']
        clients.pop(-1)
        for client in clients:
            # Clean up client data
            clean = {'Contact Name': client[0],
                     'Company Name': client[1],
                     'Lead': False if client[2] == "No" else True,
                     'Phone': client[3],
                     'Email': client[4],
                     'Billing Address': client[5],
                     'Created Date': client[6],
                     'Referred By': client[7],
                     'Customer Notes': client[8],
                     'Link': client[9][61:-10]}

            all_clients.append(clean)

    write_data('clients', all_clients)


def get_invoices():
    print("Getting Invoices")

    # NOTE: We have to fire off the time frame option as a separate request
    r = requests.get("https://secure.getjobber.com/reports/invoices", cookies=cookies, params={
        'report[range]': 'custom',
        'report[start_date]': '01/01/2015',
        'report[end_date]': '01/01/2025'
    })

    r = requests.get("https://secure.getjobber.com/reports/invoices.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_invoices = json.loads(r.content)["iTotalRecords"]
    print(f'{num_invoices} invoices found!')

    # Iterate over all invoices, 250 at once
    all_invoices = []
    for i in track(range(math.ceil(num_invoices/250)), description="Getting Invoice Data..."):
        r = requests.get("https://secure.getjobber.com/reports/invoices.json", cookies=cookies, params={
            'iDisplayStart': (i*250)+1,
            'iDisplayLength': 250
        })

        json_data = json.loads(r.content)
        invoices = json_data['aaData']
        invoices.pop(-1)
        for invoice in invoices:
            # Clean up invoice data
            url = ""

            if invoice[1] != '-':
                url = "https://secure.getjobber.com" + invoice[1].split("\"")[3]

            clean = {'Client Name': invoice[0],
                     'URL': url,
                     'Visits assigned to': invoice[2],
                     'Created': '' if invoice[3] == '-' else invoice[3],
                     'Issued': '' if invoice[4] == '-' else invoice[4],
                     'Due': '' if invoice[5] == '-' else invoice[5],
                     'Marked Paid': '' if invoice[6] == '-' else invoice[6],
                     'Invoice #': invoice[7],
                     'Subject': invoice[8],
                     'Status': invoice[9],
                     'Total': invoice[10],
                     'Tip': invoice[11],
                     'Balance': invoice[12],
                     'Tax': 0 if invoice[13] == '-' else invoice[13],
                     'Deposit': invoice[14],
                     'Discount': invoice[15],
                     'Tax Amount': invoice[16],
                     'Billing Street': invoice[17],
                     'Billing City': invoice[18],
                     'Billing State': invoice[19],
                     'Billing Zip': invoice[20],
                     'Billing Phone': invoice[21],
                     'Billing Email': invoice[22],
                     'Viewed in Client Hub': '' if invoice[23] == '-' else invoice[23],
                     'Technician Name': '' if invoice[24] is None else invoice[24],
                     'Link': invoice[25][61:-10]}

            all_invoices.append(clean)

    write_data('invoices', all_invoices)


def get_quotes():
    print("Getting Quotes")

    # NOTE: We have to fire off the time frame option as a separate request
    r = requests.get("https://secure.getjobber.com/reports/quotes", cookies=cookies, params={
        'report[range]': 'custom',
        'report[start_date]': '01/01/2015',
        'report[end_date]': '01/01/2025'
    })

    r = requests.get("https://secure.getjobber.com/reports/quotes.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_quotes = json.loads(r.content)["iTotalRecords"]
    num_quotes = 1
    print(f'{num_quotes} quotes found!')

    # Iterate over all quotes, 250 at once
    all_quotes = []
    for i in track(range(math.ceil(num_quotes / 250)), description="Getting Quote Data..."):
        r = requests.get("https://secure.getjobber.com/reports/quotes.json", cookies=cookies, params={
            'iDisplayStart': (i*250)+1,
            'iDisplayLength': 250
        })

        json_data = json.loads(r.content)
        quotes = json_data['aaData']
        quotes.pop(-1)
        for quote in quotes:
            # Clean up quote data
            url = ""
            jobnum = ""
            joburl = ""

            if quote[14] != '-':
                url = quote[14].split("\"")[5]
            if quote[7] != '-':
                jobnum = quote[7].split(">")[1].split("<")[0][1:]
                joburl = "https://secure.getjobber.com" + quote[7].split("\"")[3]

            clean = {'Client Name': quote[0],
                     'Property Address': quote[1],
                     'Drafted': quote[2],
                     'Sent': quote[3],
                     'Changes Requested': quote[4],
                     'Approved': quote[5],
                     'Converted': quote[6],
                     'Job Link': '' if quote[7] == '-' else joburl,
                     'Job #s': '' if quote[7] == '-' else jobnum,
                     'Archived': quote[8],
                     '#': quote[9],
                     'Viewed in client hub': '' if quote[10] == '-' else quote[10],
                     'Status': quote[11],
                     'Total $': quote[12],
                     'Technician Name': quote[13],
                     'Link': url}

            all_quotes.append(clean)

    write_data('quotes', all_quotes)


def get_expenses():
    print("Getting Expenses")

    # NOTE: We have to fire off the time frame option as a separate request
    r = requests.get("https://secure.getjobber.com/reports/expenses", cookies=cookies, params={
        'report[range]': 'custom',
        'report[start_date]': '01/01/2015',
        'report[end_date]': '01/01/2025'
    })

    r = requests.get("https://secure.getjobber.com/reports/expenses.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_expenses = json.loads(r.content)["iTotalRecords"]
    print(f'{num_expenses} expenses found!')

    # Iterate over all expenses, 250 at once
    all_expenses = []
    for i in track(range(math.ceil(num_expenses / 250)), description="Getting Expense Data..."):
        r = requests.get("https://secure.getjobber.com/reports/expenses.json", cookies=cookies, params={
            'iDisplayStart': (i*250)+1,
            'iDisplayLength': 250
        })

        json_data = json.loads(r.content)
        expenses = json_data['aaData']
        expenses.pop(-1)
        for expense in expenses:
            # Clean up expense data
            joblink = ""
            propertylink = ""

            if expense[5] != '':
                joblink = "https://secure.getjobber.com" + expense[5].split("\"")[3]
            if expense[6] != '':
                propertylink = "https://secure.getjobber.com" + expense[6].split("\"")[3]

            clean = {'Item Name': expense[0],
                     'Details': expense[1],
                     'Total': expense[2],
                     'Entered By': expense[3],
                     'Reimburse To': expense[4],
                     'Job Link': joblink,
                     'Property Link': propertylink,
                     'Date': expense[7],
                     'Client Name': '' if expense[8] == '' else expense[8],
                     'Job Subject': '' if expense[9] == '' else expense[9],
                     'Edit Link': expense[10][64:-10]}

            all_expenses.append(clean)

    write_data('expenses', all_expenses)


def get_data():
    get_clients()
    get_invoices()
    get_expenses()
    get_quotes()
