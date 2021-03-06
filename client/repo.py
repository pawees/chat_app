import sys

import service
import click
import dotenv
import os

class Chatty:

    host = ''
    current_chat = ''
    token = ''

    def __init__(self):
        self.dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(self.dotenv_file)
        self.host = os.environ["HOST"]
        self.current_chat = os.environ['C_CHAT']
        self.token = os.environ['TOKEN']

        res = service.test_conn(self.host)
        if res != 200 and res != 404:
            raise Exception("not connected,err_code: %s" % res)

    def set_token(self,token):
        os.environ["TOKEN"] = token
        dotenv.set_key(self.dotenv_file, "TOKEN", os.environ["TOKEN"])

    def set_current_chat(self,current):
        os.environ["C_CHAT"] = current
        dotenv.set_key(self.dotenv_file, "C_CHAT", os.environ["C_CHAT"])



S = Chatty()

def is_auth():
    if not S.token:
        click.echo("Войдите или зарегистрируйтесь.\nrepo signup --help\nrepo login --help")
        sys.exit()
    else:
        return

@click.group()
def cli():
    """Repo is a command line tool for chatting_room app
    """
@cli.command()
def list():

    is_auth()
    res = service.get_list(S.host,S.token)
    click.echo(res)

@cli.command()
@click.option("--username", prompt=True, help="The username.")
@click.password_option(help="The login password.")
def login(username, password):
    """Log in.Give current credentials.
    """
    res = service.login(S.host,username,password)
    S.set_token(res)
    click.echo("OK")

@cli.command()
@click.option("--username", prompt=True, help="The username.")
@click.option("--email", prompt="E-mail", help="The user email.")
@click.password_option(help="The login password.")
def signup(username, password,email):
    """repo signup
    """
    res = service.sign_up(S.host,username,email,password)

    S.set_token(res)

    click.echo("Пользователь успешно создан")

@cli.command()
@click.option(
    "--message",
    "-m",
    multiple=True,
    required=True,
    help="The message to send chat.",
)
def message(message):
    """
    repo message -m "Hello_word"
    """
    is_auth()

    if not S.current_chat:
        return click.echo("Вы не подписаны ни на один чат\n"
                          "repo select --help\nили\n"
                          "repo create --help")

    res = service.send_message(S.host,message,S.current_chat,S.token)
    click.echo(res)

@cli.command()
@click.option(
    "--name",
    "-n",
    multiple=True,
    required=True,
    help="New chat name",
)
def create(name):
    """
    This command create new chat.
    ex: repo create -n Chat1
    """
    is_auth()

    res = service.create_room(S.host,name[0],S.token)

    S.set_current_chat(name[0])

    click.echo(res)

@cli.command()
@click.option(
    "--chat_name",
    "-c",
    multiple=True,
    required=True,
    help="Select chat",
)
def select(chat_name):
    """
    This command select req chat.
    ex: repo select -c Chat1
    """
    is_auth()

    res = service.select_chat(S.host,chat_name[0],S.token)

    S.set_current_chat(chat_name[0])

    click.echo(res)



@cli.command()
def refresh():
    """
    This command refresh current chat.
    repo refresh -c Chat1
    """
    is_auth()

    res = service.select_chat(S.host,S.current_chat,S.token)


    click.echo(res)


@cli.command()
def logout():
    is_auth()

    S.set_token('')
    click.echo('ok')
