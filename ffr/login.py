"""This example demonstrates the flow for retrieving a refresh token.

In order for this example to work your application's redirect URI must be set
to http://localhost:8080.

This tool can be used to conveniently create refresh tokens for later use with
your web application OAuth2 credentials.

"""
import os
import sys
import socket
import random
import webbrowser
import configparser
from time import sleep

import praw
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def login():
    console.print(Markdown("# Login"))
    console.print(
        "Go here while logged into the account you want to create a token for: "
        "https://www.reddit.com/prefs/apps/"
        "\nClick the create an app button. Put something in the name field and select the"
        " script radio button."
        "\nPut http://localhost:8080 in the redirect uri field and click create app"
    )

    client_id = console.input(
        "\n[indian_red][u]Enter the [bold]Client ID[/bold][/u][/indian_red], it's the line just under Personal use script at the top: ")

    client_secret = console.input(
        "[indian_red][u]Enter the [bold]Client secret[/bold][/u][/indian_red], it's the line next to secret: ")

    username = console.input("[indian_red][u]Enter your [bold]Username[/bold][/u][/indian_red]: ")

    password = console.input("[indian_red][u]Now enter your [bold]Password[/bold][/u][/indian_red]: ")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8080",
        user_agent="saved_reddit_script",
    )

    state = str(random.randint(0, 65000))

    # Get oauth url
    url = reddit.auth.url(["identity"], state, "permanent")
    sleep(3)
    console.print(
        f"[indian_red]\nThe link to authorize this script will open in 3 seconds\nIf the url didn't open, please manually open this link[/indian_red]: ")
    webbrowser.open(url)
    # Printing the url with rich makes the terminal not recognize the entire url.
    print(url)

    # Open a socket and wait for a connection.
    sys.stdout.flush()
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            client,
            "State mismatch. Expected: {} Received: {}".format(state, params["state"]),
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1

    # Generate the praw.ini file with the provided information.
    praw_section = 'USER' if is_new_user() else username

    user_info = f"[{praw_section}]\
    \nclient_id={client_id}\
    \nclient_secret={client_secret}\
    \nusername={username}\
    \npassword={password}\n"

    dst = get_praw_conf()
    # Write info into praw.ini.
    add_to_file(dst, user_info)

    message = f"\n\nThat\'s it, everything has been pasted in the praw.ini file.\
    \nYou can find it in [bold]{dst}[/bold]\
    \nIf this is your second account, you'll have to specify the user with the --user flag."
    console.print(message)

    send_message(client, "<h1>Perfect, now you can close this tab and start using Filter for Reddit! &#128515</h1>")
    return 0


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    client.send("HTTP/1.1 200 OK\r\n\r\n{}".format(message).encode("utf-8"))
    client.close()


def add_to_file(dst, string):
    """Append the user config to praw.ini config file"""
    with open(dst, 'a') as f:
        f.write(string)
        f.write("\n")


def get_praw_conf():
    """Returns the path to the praw.ini config file"""

    # Borrowed from https://github.com/praw-dev/praw/blob/973dc8a9471a0c05e88dde9de3463b3863e6eecc/praw/settings.py#L31
    if 'APPDATA' in os.environ:  # Windows
        os_config_path = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:  # Modern Linux
        os_config_path = os.environ['XDG_CONFIG_HOME']
    elif 'HOME' in os.environ:  # Legacy Linux
        os_config_path = os.path.join(os.environ['HOME'], '.config')
    else:
        os_config_path = os.path.dirname(sys.modules[__name__].__file__)

    return os.path.join(os_config_path, 'praw.ini')


def is_new_user():
    """Return True if there is no section in the praw.ini file
    with a USER section"""
    praw_path = get_praw_conf()
    config = configparser.ConfigParser()
    config.read(praw_path)
    sections = config.sections()

    return False if 'USER' in sections else True


if __name__ == "__main__":
    login()
