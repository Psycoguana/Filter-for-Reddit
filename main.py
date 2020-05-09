import re
import time
from typing import List
from tabulate import tabulate
from prawcore.exceptions import OAuthException
from praw.models.reddit.submission import Submission
import praw.exceptions
from praw.models.reddit.base import RedditBase

LIMIT = 100

CHOICES = """What do you want to get?
1. All.
2. Self.
3. Media.
4. Specific subreddits.
5. NSFW.
6. EXTERNAL LINKS ?????????????

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


def main():
    user_input = input(CHOICES)
    saved = get_saved()

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
        else:
            print("Invalid choice")
        user_input = input(CHOICES)


def media_menu(elements):
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
    matched = get_media(elements, param)
    parse_content(matched)


def ask_for_subreddits():
    """ Asks for subreddits, splits with a + sign and returns a list """
    entered_subs = []
    user_input = input("Input your subs (wtf+python): ").split('+')
    # TODO: Replace this for loop with a list comprehension if possible
    for sub in user_input:
        entered_subs.append(sub)
    return entered_subs


def get_saved():
    """Get every saved elements and separate posts from comments"""
    # Change limit to 100 or none
    saved: List[RedditBase] = reddit.user.me().saved(limit=LIMIT)
    return saved


def parse_content(elements):
    table_data = []
    rlink = "https://www.redd.it/"

    i = 1
    for element in elements:
        print(f"Working with element #{i} of #{len(elements)}")
        if type(element) == Submission:
            sub = f"r/{element.subreddit}"
            title = element.title
            link = rlink + element.id
            table_data.append([sub, title, link])
        else:
            sub = f"r/{element.subreddit}"
            title = element.body[0:70] if len(element.body) > 71 else element.body
            link = rlink + element.id
            table_data.append([sub, title, link])
        i += 1
    _show_table(table_data)


def _show_table(table_data):
    print("Generating table")
    table = tabulate(table_data, headers=["Subreddits", "Posts and Comments", "Links"], tablefmt="psql")
    print(table)


def get_all(elements):
    all = []
    for element in elements:
        all.append(element)
    return all


def get_self(posts):
    print("get_self() called")
    self_posts = []
    i = 0
    for post in posts:
        i += 1
        if type(post) == Submission and post.is_self:
            self_posts.append(post)

    return self_posts


def get_nsfw(elements):
    # TODO: Why is this slow?
    print("get_nsfw() called")
    nsfw = []
    for element in elements:
        print(element)
        if element.subreddit.over18:
            nsfw.append(element)
    return nsfw


def get_subreddit(elements, subreddits):
    print("get_subreddit() called")
    matched_subreddits = []

    for element in elements:
        if str(element.subreddit).lower() in subreddits:
            matched_subreddits.append(element)

    return matched_subreddits


def get_media(posts, media_type):
    """Get media, it can be video, gif or img"""
    # Here we set the pattern according to the type of file we want
    if media_type == "img":
        pattern = "i.redd.it\/.+\.jpg|imgur.com\/.+\.jpg"
    elif media_type == "gif":
        # i.imgur.com/[ANYTHING].gifv
        # i.redd.it/[ANYTHING].gif
        pattern = "i.redd.it\/.+\.gif|i.imgur\.com\/.+\.gifv|gfycat"
    elif media_type == "vid":
        pattern = "pornhub.com|v\.redd\.it|youtube.com|vimeo"
    else:
        pattern = ".+"

    # Now we check each URL and save only the ones that match the previously set pattern
    matched_posts = []
    for post in posts:
        if type(post) == Submission and re.search(pattern, post.url):
            matched_posts.append(post)

    return matched_posts


if __name__ == '__main__':
    t0 = time.time()
    # TODO: Rewrite get_saved, parse content, get_all.
    # TODO: Improve menu
    # TODO: Fix slow get_nsfw()
    # TODO: Implement OAuth
    main()
    # Retrieving all saved posts
    saved = get_saved()
    print("All posts gathered")
    # get_nsfw(saved)
    print(f"Execution time: {(time.time() - t0) / 60}")
