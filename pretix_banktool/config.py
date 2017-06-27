import sys
from urllib.parse import urljoin

import click


def validate_config(config):
    validate_pretix_config(config)
    if 'banktool' not in config:
        click.echo(click.style('Invalid config file: Does not contain banktool section', fg='red'))
        sys.exit(1)
    if 'type' not in config['banktool']:
        click.echo(click.style('Invalid config file: Does not contain connection type', fg='red'))
        sys.exit(1)
    if config['banktool']['type'] == 'fints':
        validate_fints_config(config)
    else:
        click.echo(click.style('Invalid config file: Unknown type %s' % config['banktool']['type'], fg='red'))
        sys.exit(1)


def validate_fints_config(config):
    if 'fints' not in config:
        click.echo(click.style('Invalid config file: Does not contain fints section', fg='red'))
        sys.exit(1)

    for f in ('iban', 'blz', 'username', 'endpoint', 'pin'):
        if f not in config['fints']:
            click.echo(click.style('Invalid config file: Does not contain value for fints.%s' % f, fg='red'))
            sys.exit(1)


def validate_pretix_config(config):
    if 'pretix' not in config:
        click.echo(click.style('Invalid config file: Does not contain pretix section', fg='red'))
        sys.exit(1)

    for f in ('organizer', 'server', 'key'):
        if f not in config['pretix']:
            click.echo(click.style('Invalid config file: Does not contain value for pretix.%s' % f, fg='red'))
            sys.exit(1)


def get_endpoint(config):
    return urljoin(
        config['pretix']['server'],
        '/api/v1/organizers/{}/bankimportjobs/'.format(config['pretix']['organizer'])
    )


def get_pin(config):
    return config['fints']['pin'] or click.prompt('Your online-banking PIN', hide_input=True)
