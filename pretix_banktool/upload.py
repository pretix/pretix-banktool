import sys
from datetime import date, timedelta

import click
import re
import requests
from fints.client import FinTS3PinTanClient
from pretix_banktool.config import get_endpoint, get_pin
from pretix_banktool.parse import join_reference, parse_transaction_details
from requests import RequestException


def upload_transactions(config, days=30, ignore=None):
    ignore = ignore or []
    ignore_patterns = []
    for i in ignore:
        try:
            ignore_patterns.append(re.compile(i))
        except re.error as e:
            click.echo(click.style('Not a valid regular expression: %s' % i, fg='red'))
            click.echo(click.style('"%s" at position %d' % (e.msg, e.pos), fg='red'))

    click.echo('Creating FinTS client...')
    f = FinTS3PinTanClient(
        config['fints']['blz'],
        config['fints']['username'],
        get_pin(config),
        config['fints']['endpoint'],
    )

    click.echo('Fetching SEPA account list...')
    accounts = f.get_sepa_accounts()
    click.echo('Looking for correct SEPA account...')
    accounts_matching = [a for a in accounts if a.iban == config['fints']['iban']]
    if not accounts_matching:
        click.echo(click.style('The specified SEPA account %s could not be found.' % config['fints']['iban'],
                               fg='red'))
        click.echo('Only the following SEPA accounts were detected:')
        click.echo(', '.join([a.iban for a in accounts]))
        sys.exit(1)
    elif len(accounts_matching) > 1:
        click.echo(click.style('Multiple SEPA accounts match the given IBAN. We currently can not handle this '
                               'situation.',
                               fg='red'))
        click.echo('Only the following SEPA accounts were detected:')
        click.echo(', '.join([a.iban for a in accounts]))
        sys.exit(1)

    account = accounts_matching[0]
    click.echo(click.style('Found matching SEPA account.', fg='green'))

    click.echo('Fetching statement of the last %d days...' % days)
    statement = f.get_statement(account, date.today() - timedelta(days=days), date.today())
    if statement:
        click.echo(click.style('Found %d transactions.' % len(statement), fg='green'))
        click.echo('Parsing...')

        transactions = []
        ignored = 0
        for transaction in statement:
            transaction_details = parse_transaction_details(transaction.data['transaction_details'])
            payer = {
                'name': transaction_details.get('accountholder', ''),
                'iban': transaction_details.get('accountnumber', ''),
            }
            reference, eref = join_reference(transaction_details.get('reference', '').split('\n'), payer)
            if not eref:
                eref = transaction_details.get('eref', '')

            ignore = False
            for i in ignore_patterns:
                if i.search(reference):
                    ignore = True
                    ignored += 1
                    break

            if not ignore:
                transactions.append({
                    'amount': str(transaction.data['amount'].amount),
                    'reference': reference + (' EREF: {}'.format(eref) if eref else ''),
                    'payer': (payer.get('name', '') + ' - ' + payer.get('iban', '')).strip(),
                    'date': transaction.data['date'].isoformat(),
                })

        if ignored > 0:
            click.echo(click.style('Ignored %d transactions.' % ignored, fg='blue'))
        payload = {
            'event': None,
            'transactions': transactions
        }

        click.echo('Uploading...')
        try:
            r = requests.post(get_endpoint(config), headers={
                'Authorization': 'Token {}'.format(config['pretix']['key'])
            }, json=payload)
            if r.status_code == 201:
                click.echo(click.style('Job uploaded.', fg='green'))
            else:
                click.echo(click.style('Invalid response code: %d' % r.status_code, fg='red'))
                click.echo(r.text)
                sys.exit(2)
        except (RequestException, OSError) as e:
            click.echo(click.style('Connection error: %s' % str(e), fg='red'))
            sys.exit(2)
        except ValueError as e:
            click.echo(click.style('Could not read response: %s' % str(e), fg='red'))
            sys.exit(2)
    else:
        click.echo('No recent transaction found.')
