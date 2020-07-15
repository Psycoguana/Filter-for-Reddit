import re
from rich import box
from rich.progress import track
from rich.console import Console
from rich.table import Column, Table
import click
from typing import List
from tabulate import tabulate
from prawcore.exceptions import OAuthException
from praw.models.reddit.submission import Submission
from praw.models.reddit.comment import Comment
import praw.exceptions
from praw.models.reddit.base import RedditBase

# TODO: Rewrite get_saved, parse content, get_all.
# TODO: Improve menu
# TODO: Implement OAuth

LIMIT = 50

# TODO: External Links.
CHOICES = """What do you want to get?
1. All.
2. Self.
3. Media.
4. Specific subreddits.
5. NSFW.
6. Just Posts.
7. Just Comments.
8. Search Post's Titles
9. Search in Comments
10. External Websites

0. Exit.
"""
MEDIA_CHOICES = """1. Images
2. Gifs
3. Videos
4. All of the above

0. Return"""

reddit = praw.Reddit('USER', user_agent='saved_reddit_script')
try:
    user = reddit.user.me()
except OAuthException:
    raise Exception("OAuthException: Wrong username or password")

print(f"Hello {user}")


class Filter:

    def __init__(self):
        self.saved = ""

    def initialize(self):
        self.saved = self.get_saved()

    def main(self):
        user_input = input(CHOICES)
        saved = self.get_saved()
        print("")

        while user_input != '0':
            if user_input == '1':
                matched = get_all(saved)
                parse_content(matched)
            elif user_input == '2':
                matched = get_self(saved)
                parse_content(matched)
            elif user_input == '3':
                media_menu(saved)
            elif user_input == '4':
                subs = ask_for_subreddits()
                matched = get_subreddit(saved, subs)
                parse_content(matched)
            elif user_input == '5':
                matched = get_nsfw(saved)
                parse_content(matched)
            elif user_input == '6':
                matched = get_posts(saved)
                parse_content(matched)
            elif user_input == '7':
                matched = get_comments(saved)
                parse_content(matched)
            elif user_input == '8':
                query = input("What do you want to search: ")
                print("")
                matched = search_posts(saved, query)
                parse_content(matched)
            elif user_input == '9':
                query = input("What do you want to search: ")
                print("")
                matched = search_comments(saved, query)
                parse_content(matched)
            elif user_input == '10':
                matched = get_external_links(saved)
                parse_content(matched)
            else:
                print("Invalid choice")
            user_input = input(CHOICES)

    def media_menu(self, elements):
        user_input = input(MEDIA_CHOICES)
        param = ""
        if user_input == '1':
            param = "img"
        elif user_input == '2':
            param = "gif"
        elif user_input == '3':
            param = "vid"
        elif user_input == '4':
            param = "all"
        matched = self.get_media(elements, param)
        self.parse_content(matched)

    def get_saved(self):
        """Get every saved elements and separate posts from comments"""
        # Change limit to 100 or none
        saved: List[RedditBase] = reddit.user.me().saved(limit=LIMIT)
        return saved

    def parse_content(self, elements):
        table_data = []
        rlink = "https://www.reddit.com/"

        i = 1
        for element in elements:
            if type(element) == Submission:
                sub = f"r/{element.subreddit}"
                title = element.title[0:134] if len(
                    element.title) > 135 else element.title
                link = rlink + element.id
                title = f"[link={link}]{title}[\link]"
                table_data.append([sub, title, link])
            else:
                sub = f"r/{element.subreddit}"
                title = element.body[0:134] + \
                        "..." if len(element.body) > 135 else element.body
                # Makes comments a little bit tidier by removing new lines.
                title = " ".join(title.split())
                # TODO: Fix link
                # link = f"{rlink}r/{sub}/comments/{element}/-/{element.id}"
                link = "https://www.reddit.com" + str(element.permalink)
                table_data.append([sub, title, link])
            i += 1
        if table_data:
            self._show_table(table_data)
        else:
            print("There was nothing found for this query :/")

    def _show_table(self, table_data):
        table = Table(title="Matched Posts", show_header=True, header_style="bold red", box=box.HEAVY)
        table.add_column("Subreddits", justify='left')
        table.add_column("Posts and Comments", justify='center')
        table.add_column("Links", justify='right')
        for i, _ in enumerate(table_data):
            table.add_row(*table_data[i])
        Console().print(table)

    def get_all(self):
        all = []
        for element in self.saved:
            all.append(element)
        return all

    def get_self(self):
        print("get_self() called")
        self_posts = []
        i = 0
        for element in self.saved:
            i += 1
            if type(element) == Submission and element.is_self:
                self_posts.append(element)

        return self_posts

    def get_nsfw(self):
        nsfw = []
        for element in self.saved:
            if element.over_18:
                nsfw.append(element)
            return nsfw

    def get_subreddit(self, subreddits):
        print("get_subreddit() called")
        matched_subreddits = []

        for element in self.saved:
            if str(element.subreddit).lower() in subreddits:
                matched_subreddits.append(element)

        return matched_subreddits

    def get_media(self, media_type):
        """Get media, it can be video, gif or img"""
        # Here we set the pattern according to the type of file we want
        if media_type == "img":
            pattern = "i.redd.it\/.+\.(jpg|jpeg|png)|imgur.com\/.+\.(jpg|jpeg|png)"
        elif media_type == "gif":
            # i.imgur.com/[ANYTHING].gifv
            # i.redd.it/[ANYTHING].gif
            pattern = "i.redd.it\/.+\.gif|i.imgur\.com\/.+\.gifv|gfycat"
        elif media_type == "vid":
            # This could be improved, don't know how tho
            pattern = "pornhub.com|v\.redd\.it|youtube.com|vimeo"
        else:  # TODO: Maybe raise an error?
            pattern = ".+"

        # Now we check each URL and save only the ones that match
        # the previously set pattern.
        matched_posts = []
        for element in self.saved:
            if type(element) == Submission and re.search(pattern, element.url):
                matched_posts.append(element)

        return matched_posts

    def get_external_links(self):
        posts = []
        # This should match any website that is not: Reddit, Imgur, Gfycat, Youtube, Pornhub or Vimeo
        # aka External sites that don't belong in media.
        # I suck at regex, so if anyone wants to improve this in any way, I'm up for it :)

        pattern = "^(?!(https?:\/\/)?(www\.)?((i\.|v\.)?(redd|imgur|reddit|gfycat|youtube|youtu|pornhub|vimeo)\.(com|it|net|gif|jpg|jpeg|png|be).+)).+$"

        for element in self.saved:
            if type(element) == Submission:
                if re.search(pattern, element.url):
                    posts.append(element)
        return posts

    def ask_for_subreddits(self):
        """ Asks for subreddits, splits with a + sign and returns a list """
        entered_subs = []
        user_input = input("Input your subs (wtf+python): ").split('+')
        # TODO: Replace this for loop with a list comprehension if possible
        for sub in user_input:
            entered_subs.append(sub)
        return entered_subs

    def get_posts(self):
        click.echo("get_posts called")
        posts = []
        for element in self.saved:
            if type(element) == Submission:
                posts.append(element)
        return posts

    def get_comments(self):
        comments = []
        for element in self.saved:
            if type(element) == Comment:
                comments.append(element)
        return comments

    def search_posts(self, query):
        posts = self.get_posts()
        matched_posts = []

        for post in posts:
            if query.lower() in str(post.title).lower():
                matched_posts.append(post)
        return matched_posts

    def search_comments(self, query):
        comments = self.get_comments()
        matched_comments = []

        for comment in comments:
            if query.lower() in str(comment.body).lower():
                matched_comments.append(comment)
        return matched_comments


@click.group()
def cli():
    pass


@cli.command()
def show_all():
    a = Filter.get_all()
    Filter.parse_content(a)


@cli.command()
@click.argument('query')
def search_post(query):
    matched = Filter.search_posts(query)
    Filter.parse_content(matched)

@cli.command()
def get_posts():
    matched = Filter.get_posts()
    Filter.parse_content(matched)


@cli.command()
def get_comments():
    matched = Filter.get_comments()
    Filter.parse_content(matched)


if __name__ == '__main__':
    # TODO: Think how not to call get_saved if im just passing the --help flag
    Filter = Filter()
    Filter.initialize()
    cli()




    # matched = search_posts(saved)
    # # matched = get_comments(saved)
