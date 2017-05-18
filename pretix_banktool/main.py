import configparser

import click


@click.group()
def main():
    pass


@main.command()
@click.option('--type', type=click.Choice(['fints']), default='fints')
def setup(type):
    click.echo(click.style('Welcome to the pretix-banktool setup!', fg='green'))

    if type == 'fints':
        click.echo('You will now be prompted all information required to setup a FinTS account for pretix.')
        click.echo('')
        click.echo(click.style('Banking information', fg='blue'))
        blz = click.prompt('Your bank\'s BLZ')
        endpoint = click.prompt('Your bank\'s FinTS endpount URL')
        username = click.prompt('Your online-banking username')
        pin = click.prompt('Your online-banking PIN', hide_input=True)

    click.echo('')
    click.echo(click.style('pretix information', fg='blue'))
    api_server = click.prompt('pretix Server', default='https://pretix.eu/')
    api_organizer = click.prompt('Short name of your organizer account', type=click.STRING)
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
    click.echo('')
    click.echo('You can now run')
    click.echo('    pretix-banktool test %s' % filename)
    click.echo('to test the connection to your bank account.')
