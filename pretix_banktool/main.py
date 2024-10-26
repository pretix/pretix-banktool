import configparser
from urllib.parse import urljoin

import click
from pretix_banktool.upload import upload_transactions

from .config import validate_config
from .testing import test_fints, test_pretix


@click.group()
def main():
    pass


@main.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--fints/--no-fints', default=True, help='Test FinTS connection')
@click.option('--pretix/--no-pretix', default=True, help='Test pretix connection')
def test(configfile, fints, pretix):
    config = configparser.ConfigParser()
    config.read(configfile)
    validate_config(config)
    if config['banktool']['type'] == 'fints' and fints:
        test_fints(config)
    if pretix:
        test_pretix(config)


@main.command()
@click.argument('configfile', type=click.Path(exists=True))
@click.option('--days', default=30, help='Number of days to go back.')
@click.option('--pending/--no-pending', default=False, help='Include pending transactions.')
@click.option('--bank-ids/--no-bank-ids', default=False, help='Include transaction IDs given by bank.')
@click.option('--ignore', help='Ignore all references that match the given regular expression. '
                               'Can be passed multiple times.', multiple=True)
def upload(configfile, days, pending, bank_ids, ignore):
    config = configparser.ConfigParser()
    config.read(configfile)
    validate_config(config)
    upload_transactions(config, days, pending, bank_ids, ignore)


@main.command()
@click.option('--type', type=click.Choice(['fints']), default='fints')
def setup(type):
    click.echo(click.style('Welcome to the pretix-banktool setup!', fg='green'))

    if type == 'fints':
        click.echo('You will now be prompted all information required to setup a FinTS account for pretix.')
        click.echo('')
        click.echo(click.style('Banking information', fg='blue'))
        blz = click.prompt('Your bank\'s BLZ')
        iban = click.prompt('Your account IBAN')
        endpoint = click.prompt('Your bank\'s FinTS endpount URL')
        username = click.prompt('Your online-banking username')
        click.echo(click.style('WARNING: If you enter your PIN here, it will be stored in clear text on your disk. '
                               'If you leave it empty, you will instead be asked for it every time.', fg='yellow'))
        pin = click.prompt('Your online-banking PIN', hide_input=True, default='', show_default=False)

    click.echo('')
    click.echo(click.style('pretix information', fg='blue'))
    api_server = click.prompt('pretix Server', default='https://pretix.eu/')
    api_organizer = click.prompt('Short name of your organizer account', type=click.STRING)
    click.echo('You will now need an API key. If you do not have one yet, you can create one as part of a team here:')
    click.echo(urljoin(api_server, '/control/organizer/{}/teams'.format(api_organizer)))
    click.echo('The key needs to created for a team with the permissions "can view orders" and "can change orders" '
               'for all events that you want to match orders with.')
    api_key = click.prompt('API key')

    click.echo('')
    click.echo(click.style('Other information', fg='blue'))
    filename = click.prompt('Configuration file', default=api_organizer + '.cfg', type=click.Path(exists=False))

    config = configparser.ConfigParser()
    config['banktool'] = {
        'type': type
    }
    if type == 'fints':
        config['fints'] = {
            'blz': blz,
            'endpoint': endpoint,
            'username': username,
            'iban': iban,
            'pin': pin
        }
    config['pretix'] = {
        'server': api_server,
        'organizer': api_organizer,
        'key': api_key
    }
    with open(filename, 'w') as configfile:
        config.write(configfile)

    click.echo('')
    click.echo(click.style('Configuration file created!', fg='green'))
    click.echo(click.style('Please note that your pin has been saved to the file in plain text. Make sure to secure '
                           'the file appropriately.',
                           fg='red'))
    click.echo('')
    click.echo('You can now run')
    click.echo('    pretix-banktool test %s' % filename)
    click.echo('to test the connection to your bank account.')
