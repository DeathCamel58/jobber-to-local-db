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

retrieve_at_once = int(configuration_file.get('jobber', 'retrieve_at_once'))

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

    # Iterate over all clients
    all_clients = []
    for i in track(range(math.ceil(num_clients/retrieve_at_once)), description="Getting Client Data..."):
        r = requests.get("https://secure.getjobber.com/reports/clients.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
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

    # Iterate over all invoices
    all_invoices = []
    for i in track(range(math.ceil(num_invoices/retrieve_at_once)), description="Getting Invoice Data..."):
        r = requests.get("https://secure.getjobber.com/reports/invoices.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
        })

        json_data = json.loads(r.content)
        invoices = json_data['aaData']
        invoices.pop(-1)
        for invoice in invoices:
            # Clean up invoice data
            joburl = ""
            jobnum = ""

            if invoice[1] != '-':
                joburl = "https://secure.getjobber.com" + invoice[1].split("\"")[3]
                jobnum = invoice[1].split("#")[1].split("<")[0]

            clean = {'Client Name': invoice[0],
                     'Job Link': joburl,
                     'Job Numbers': jobnum,
                     'Visits assigned to': invoice[2],
                     'Created': '' if invoice[3] == '-' else invoice[3],
                     'Issued': '' if invoice[4] == '-' else invoice[4],
                     'Due': '' if invoice[5] == '-' else invoice[5],
                     'Marked Paid': '' if invoice[6] == '-' else invoice[6],
                     'Invoice Number': invoice[7],
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
    print(f'{num_quotes} quotes found!')

    # Iterate over all quotes
    all_quotes = []
    for i in track(range(math.ceil(num_quotes / retrieve_at_once)), description="Getting Quote Data..."):
        r = requests.get("https://secure.getjobber.com/reports/quotes.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
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
                jobnum = quote[7].split("#")[1].split("<")[0]
                joburl = "https://secure.getjobber.com" + quote[7].split("\"")[3]

            clean = {'Client Name': quote[0],
                     'Property Address': quote[1],
                     'Drafted': quote[2],
                     'Sent': quote[3],
                     'Changes Requested': quote[4],
                     'Approved': quote[5],
                     'Converted': quote[6],
                     'Job Link': '' if quote[7] == '-' else joburl,
                     'Job Numbers': '' if quote[7] == '-' else jobnum,
                     'Archived': quote[8],
                     'Quote Number': quote[9],
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

    # Iterate over all expenses
    all_expenses = []
    for i in track(range(math.ceil(num_expenses / retrieve_at_once)), description="Getting Expense Data..."):
        r = requests.get("https://secure.getjobber.com/reports/expenses.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
        })

        json_data = json.loads(r.content)
        expenses = json_data['aaData']
        expenses.pop(-1)
        for expense in expenses:
            # Clean up expense data
            joblink = ""
            jobnum = ""
            propertylink = ""

            if expense[5] != '':
                joblink = "https://secure.getjobber.com" + expense[5].split("\"")[3]
                jobnum = expense[5].split("#")[1].split("<")[0]
            if expense[6] != '':
                propertylink = "https://secure.getjobber.com" + expense[6].split("\"")[3]

            clean = {'Item Name': expense[0],
                     'Details': expense[1],
                     'Total': expense[2],
                     'Entered By': expense[3],
                     'Reimburse To': expense[4],
                     'Job Link': joblink,
                     'Job Numbers': jobnum,
                     'Property Link': propertylink,
                     'Date': expense[7],
                     'Client Name': '' if expense[8] == '' else expense[8],
                     'Job Subject': '' if expense[9] == '' else expense[9],
                     'Edit Link': expense[10][64:-10]}

            all_expenses.append(clean)

    write_data('expenses', all_expenses)


def get_transactions():
    print("Getting Transactions")

    # NOTE: We have to fire off the time frame option as a separate request
    r = requests.get("https://secure.getjobber.com/reports/transactions", cookies=cookies, params={
        'report[range]': 'custom',
        'report[start_date]': '01/01/2015',
        'report[end_date]': '01/01/2025'
    })

    r = requests.get("https://secure.getjobber.com/reports/transactions.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_transactions = json.loads(r.content)["iTotalRecords"]
    print(f'{num_transactions} transactions found!')

    # Iterate over all transactions
    all_transactions = []
    for i in track(range(math.ceil(num_transactions / retrieve_at_once)), description="Getting Transaction Data..."):
        r = requests.get("https://secure.getjobber.com/reports/transactions.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
        })

        json_data = json.loads(r.content)
        transactions = json_data['aaData']
        transactions.pop(-1)
        for transaction in transactions:
            # Clean up transaction data
            url = ""

            if transaction[12] != '':
                url = transaction[12].split("\"")[5]

            clean = {'Client Name': transaction[0],
                     'Date': transaction[1],
                     'Type': transaction[2],
                     'Total': transaction[3],
                     'Tip': transaction[4],
                     'Note': transaction[5],
                     'Check Number': transaction[6],
                     'Invoice Number': transaction[7],
                     'Method': transaction[8],
                     'Transaction ID': transaction[9],
                     'Transaction Number': transaction[10],
                     'Confirmation Number': transaction[11],
                     'Link': url}

            all_transactions.append(clean)

    write_data('transactions', all_transactions)


def get_one_off_jobs():
    print("Getting One-Off Jobs")

    # NOTE: We have to fire off the time frame option as a separate request
    r = requests.get("https://secure.getjobber.com/reports/one_off_jobs", cookies=cookies, params={
        'report[range]': 'custom',
        'report[start_date]': '01/01/2015',
        'report[end_date]': '01/01/2025'
    })

    r = requests.get("https://secure.getjobber.com/reports/one_off_jobs.json", cookies=cookies, params={
        'iDisplayStart': 0,
        'iDisplayLength': 1
    })

    num_jobs = json.loads(r.content)["iTotalRecords"]
    print(f'{num_jobs} One-Off jobs found!')

    # Iterate over all One-Off jobs
    all_jobs = []
    for i in track(range(math.ceil(num_jobs / retrieve_at_once)), description="Getting One-Off Job Data..."):
        r = requests.get("https://secure.getjobber.com/reports/one_off_jobs.json", cookies=cookies, params={
            'iDisplayStart': (i*retrieve_at_once)+1,
            'iDisplayLength': retrieve_at_once
        })

        json_data = json.loads(r.content)
        jobs = json_data['aaData']
        jobs.pop(-1)
        for job in jobs:
            # Clean up job data
            url = ""

            if job[11] != '':
                url = job[11].split("\"")[5]

            clean = {'Created': job[0],
                     'Client Name': job[1],
                     'Title': job[2],
                     'Scheduled': job[3],
                     'Completed': '' if job[4] == '-' else job[4],
                     'Job Number': job[5],
                     'Visits assigned to': job[6],
                     'Total $': job[7],
                     'Client Email': job[8],
                     'Job Site': job[9],
                     'Technician Name': job[10],
                     'Link': url}

            all_jobs.append(clean)

    write_data('one-off-jobs', all_jobs)


def get_data():
    get_clients()
    get_invoices()
    get_expenses()
    get_quotes()
    get_transactions()
    get_one_off_jobs()
