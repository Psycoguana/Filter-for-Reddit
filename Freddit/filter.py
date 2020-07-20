import re
import os
import sys
import praw.exceptions
from rich import box
from rich.console import Console
from rich.table import Table
from praw.models.reddit.comment import Comment
from praw.models.reddit.submission import Submission
from praw.exceptions import ClientException
from prawcore.exceptions import ResponseException, OAuthException
from configparser import DuplicateSectionError, NoSectionError, ParsingError


# TODO: Improve menu

LIMIT = 50

# TODO: External Links.
CHOICES = """What do you want to get?
1. Get every Posts and Comment.
2. Get every Post.
3. Get every Comment.
4. Get Text-Only Posts.
5. Get Posts with Media.
6. Filter specific subreddits.
7. Search in Post's Titles.
8. Search in Comments.
9. Filter NSFW.
10. Posts with external websites.

0. Exit.\n\n"""

MEDIA_CHOICES = """1. Images
2. Gifs
3. Videos
4. All of the above (Not working...)

0. Return"""


class Filter:

    def __init__(self, user='USER'):
        self.user = user
        self.saved = self.get_saved()

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        self._clear_screen()
        user_input = input(CHOICES)
        matched = []
        print("")

        while user_input != '0':
            if user_input == '1':
                matched = self.get_all()
            elif user_input == '2':
                matched = self.get_posts()
            elif user_input == '3':
                matched = self.get_comments()
            elif user_input == '4':
                matched = self.get_self()
            elif user_input == '5':
                matched = self.media_menu()
            elif user_input == '6':
                subs = self.ask_for_subreddits()
                matched = self.get_subreddit(subs)
            elif user_input == '7':
                print("What do you want to search: ", end='')
                query = input()
                print("")
                matched = self.search_posts(query)
            elif user_input == '8':
                print("What do you want to search: ", end='')
                query = input()
                print("")
                matched = self.search_comments(query)
            elif user_input == '9':
                matched = self.get_nsfw()
            elif user_input == '10':
                matched = self.get_external_links()
            else:
                print("Invalid choice")
            
            self.parse_content(matched)
            sys.exit(0)

    def ask_for_subreddits(self):
        """ Asks for subreddits, splits with a + sign and returns a list """
        entered_subs = []
        print("Input your subs (wtf, python): ")
        user_input = input().split(',')

        for sub in user_input:
            entered_subs.append(sub.strip())
        return entered_subs

    def media_menu(self):
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
        return self.get_media(param)        

    def get_saved(self):
        """Returns every saved element as a list of RedditBase"""
        try:
            reddit = praw.Reddit(self.user, user_agent='saved_reddit_script')
            return reddit.user.me().saved(limit=LIMIT)
        except NoSectionError:
            print("Please make sure the name of the praw.ini configuration exist, is not empty and written correctly.")
            sys.exit()

        except ParsingError as e:
            e = str(e).split("\n")
            print(f"The praw.ini file is not written correctly. An error was found in {e[1]}")
            sys.exit()

        except DuplicateSectionError as e:
            print(
                f"Error found on line {e.args[2]} on the configuration file praw.ini"
                f"\nAre you trying to use two or more account with the username {e.args[0]}?")
            sys.exit()

        except ResponseException as e:
            print(f"{e.args[0]}. Is your praw.ini file well written?")
            sys.exit()

        except ClientException as e:
            e = str(e).split("\n")
            print(f"{e[0]}. Please check your praw.ini file.")
            sys.exit()

        except OAuthException:
            print("Something went wrong while retrieving your saved elements. Are your password and username correct?")
            sys.exit()

        except AttributeError:
            print("Something went wrong while retrieving your saved elements. Are your password and username correct?")
            sys.exit()

    def parse_content(self, elements):
        """Parse content, showing a short title or comment body, also creating a direct link, then call _show_table"""
        table_data = []
        rlink = "https://www.reddit.com"

        for i, element in enumerate(elements):
            if type(element) == Submission:
                title = element.title[0:134] if len(element.title) > 135 else element.title
                link = rlink + "/" + element.id
            else:
                title = element.body[0:200] + "..." if len(element.body) > 201 else element.body
                # Makes comments a little bit tidier by removing new lines.
                title = " ".join(title.split())
                link = rlink + str(element.permalink)

            # These lines embed the link so rich can make a clickable text.
            sub = f"r/{element.subreddit}"
            sub = f"[link={rlink}/{sub}]{sub}[\link]"
            title = f"[link={link}]{title}[\link]"

            table_data.append([sub, title])

        if table_data:
            self._show_table(table_data)
        else:
            print("There was nothing found for this query :/")

    def _show_table(self, table_data):
        table = Table(header_style="bold red", box=box.ROUNDED)
        table.add_column("Subreddits", justify='left')
        table.add_column("Posts and Comments", justify='center')

        for i, _ in enumerate(table_data):
            table.add_row(*table_data[i])

        self._clear_screen()
        Console().print(table)

    def get_all(self):
        """Just return every saved item, no filter applied."""
        return [x for x in self.saved]

    def get_self(self):
        self_posts = []
        for element in self.saved:
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
        matched_subreddits = []
        for element in self.saved:
            if str(element.subreddit).lower() in subreddits:
                matched_subreddits.append(element)

        return matched_subreddits

    def get_media(self, media_type):
        """Get media, it can be video, gif or image"""
        # Here we set the pattern according to the type of file we want
        if media_type == "img":
            pattern = r"i.redd.it\/.+\.(jpg|jpeg|png)|imgur.com\/.+\.(jpg|jpeg|png)"
        elif media_type == "gif":
            # i.imgur.com/[ANYTHING].gifv
            # i.redd.it/[ANYTHING].gif
            pattern = r"i.redd.it\/.+\.gif|i.imgur\.com\/.+\.gifv|gfycat"
        elif media_type == "vid":
            # This could be improved, don't know how tho
            pattern = r"pornhub.com|v\.redd\.it|youtube.com|vimeo"
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

        pattern = r"^(?!(https?:\/\/)?(www\.)?((i\.|v\.)?(redd|imgur|reddit|gfycat|youtube|youtu|pornhub|vimeo)\.(com|it|net|gif|jpg|jpeg|png|be).+)).+$"

        for element in self.saved:
            if type(element) == Submission:
                if re.search(pattern, element.url):
                    posts.append(element)
        return posts

    def get_posts(self):
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
        # TODO: Improve search, things like "tip" don't show up.
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


if __name__ == '__main__':
    Filter()
