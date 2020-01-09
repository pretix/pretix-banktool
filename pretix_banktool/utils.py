import click
from fints.client import NeedTANResponse
from fints.hhd.flicker import terminal_flicker_unix


def ask_for_tan(f, response):
    if not isinstance(response, NeedTANResponse):
        return response
    click.echo(click.style("A TAN is required", fg="red"))
    click.echo(response.challenge)
    if getattr(response, 'challenge_hhduc', None):
        try:
            terminal_flicker_unix(response.challenge_hhduc)
        except KeyboardInterrupt:
            pass
    tan = input('Please enter TAN:')
    return f.send_tan(response, tan)
