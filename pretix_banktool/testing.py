import pprint
import sys
from datetime import date, timedelta

import click
import requests
from fints.client import FinTS3PinTanClient, FinTSClientMode
from pretix_banktool import __version__
from requests import RequestException

from .config import get_endpoint, get_pin
from .utils import ask_for_tan


def test_fints(config):
    click.echo('Creating FinTS client...')
    f = FinTS3PinTanClient(
        config['fints']['blz'],
        config['fints']['username'],
        get_pin(config),
        config['fints']['endpoint'],
        mode=FinTSClientMode.INTERACTIVE,
        product_id='459BE10AAEE93C6AA90BE6FE3',
        product_version=__version__
    )

    if not f.get_current_tan_mechanism():
        f.fetch_tan_mechanisms()
        mechanisms = list(f.get_tan_mechanisms().items())
        if len(mechanisms) > 1:
            click.echo("Multiple tan mechanisms available:")
            s = None
            for i, m in enumerate(mechanisms):
                click.echo("Function {p.security_function}: {p.name}".format(p=m[1]))
                if i == 0 or m[1].security_function == config['fints'].get('security_function'):
                    s = m[0]

            if not config['fints'].get('security_function'):
                click.echo("Choosing first one since 'security_function' is not set in config file.")
            f.set_tan_mechanism(s)
        else:
            f.set_tan_mechanism(mechanisms[0][0])

    if f.is_tan_media_required() and not f.selected_tan_medium:
        with f:
            m = f.get_tan_media()
        if len(m[1]) == 1:
            f.set_tan_medium(m[1][0])
        else:
            click.echo("Multiple tan media available:")
            s = None
            for i, mm in enumerate(m[1]):
                print(i,
                      "Medium {p.tan_medium_name}: Phone no. {p.mobile_number_masked}, Last used {p.last_use}".format(
                          p=mm))
                if i == 0 or mm.tan_medium_name == config['fints'].get('tan_medium'):
                    s = mm
            if not config['fints'].get('tan_medium'):
                click.echo("Choosing first one since 'tan_medium' is not set in config file.")
            f.set_tan_medium(s)

    with f:
        if f.init_tan_response:
            ask_for_tan(f, f.init_tan_response)

        click.echo('Fetching SEPA account list...')
        accounts = ask_for_tan(f, f.get_sepa_accounts())
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

        click.echo('Fetching statement of the last 14 days...')
        statement = ask_for_tan(f, f.get_transactions(account, date.today() - timedelta(days=14), date.today()))
        if statement:
            click.echo(click.style('Found %d transactions. The last one is:' % len(statement), fg='green'))
            pprint.pprint(statement[-1].data)
        else:
            click.echo('No recent transaction found. Please check if this is correct.')


def test_pretix(config):
    click.echo('Testing pretix connection...')
    try:
        r = requests.get(get_endpoint(config), headers={
            'Authorization': 'Token {}'.format(config['pretix']['key'])
        }, verify=not config.getboolean('pretix', 'insecure', fallback=False))
        if 'results' in r.json():
            click.echo(click.style('Connection successful.', fg='green'))
        else:
            click.echo(click.style('Could not read response: %s' % str(r.text), fg='red'))
    except (RequestException, OSError) as e:
        click.echo(click.style('Connection error: %s' % str(e), fg='red'))
    except ValueError as e:
        click.echo(click.style('Could not read response: %s' % str(e), fg='red'))
