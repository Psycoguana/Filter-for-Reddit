"""This example demonstrates the flow for retrieving a refresh token.

In order for this example to work your application's redirect URI must be set
to http://localhost:8080.

This tool can be used to conveniently create refresh tokens for later use with
your web application OAuth2 credentials.

"""
import os
import pathlib
import random

import praw


def login():
    print(
        "Go here while logged into the account you want to create a token for: "
        "https://www.reddit.com/prefs/apps/"
    )
    print(
        "Click the create an app button. Put something in the name field and select the"
        " script radio button."
    )
    print("Put http://localhost:8080 in the redirect uri field and click create app")

    print("\nEnter the client ID, it's the line just under Personal use script at the top: ", end='')
    client_id = input()

    print("Enter the client secret, it's the line next to secret: ", end='')
    client_secret = input()

    print("Enter your username: ", end='')
    username = input()
    print("Now enter your password: ", end='')
    password = input()

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8080",
        user_agent="saved_reddit_script",
    )

    state = str(random.randint(0, 65000))

    url = reddit.auth.url(["identity"], state, "permanent")
    print("\nNow open this url in your browser: " + url)

    user_info = f"""[USER]
client_id={client_id}
client_secret={client_secret}
username={username}
password={password}\n
"""
    print("\n\nThat's it, everything's been pasted in the praw.ini file"
          "\nIf this is your second account, please edit the [USER] in the file with something else")
    add_to_file(user_info)
    return 0


def add_to_file(string):
    """Append the user config to praw.ini config file"""

    # This sets the Current Working Directory to wherever the script is located.
    # Ensuring the script gets the correct path of praw.ini no matter from where it's called.
    script_dir = pathlib.Path(__file__).parent.absolute()
    os.chdir(script_dir)

    with open('./praw.ini', 'a') as f:
        f.write("\n")
        f.write(string)


if __name__ == "__main__":
    login()
