import pprint
import sys
from datetime import date, timedelta

import click
from fints.client import FinTS3PinTanClient


def test_fints(config):
    click.echo('Creating FinTS client...')
    f = FinTS3PinTanClient(
        config['fints']['blz'],
        config['fints']['username'],
        config['fints']['pin'],
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

    click.echo('Fetching statement of the last 30 days...')
    statement = f.get_statement(account, date.today() - timedelta(days=30), date.today())
    if statement:
        click.echo(click.style('Found %d transactions. The last one is:' % len(statement), fg='green'))
        pprint.pprint(statement[-1].data)
    else:
        click.echo('No recent transaction found. Please check if this is correct.')
