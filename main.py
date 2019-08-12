import re
import time
import praw
from praw.models.reddit.submission import Submission
from praw.models.reddit.comment import Comment

reddit = praw.Reddit('USER', user_agent='saved_reddit_script')
user = reddit.user.me()

print(f"Hello {user}")


def get_saved():
    """Get every saved elements and separate posts from comments"""
    saved = reddit.redditor(str(user)).saved(limit=50)

    posts = []
    comments = []
    saved_all = []

    for x in saved:
        saved_all.append(x)

        if type(x) == Submission:
            posts.append(x)
        else:
            comments.append(x)

    return saved_all, posts, comments


def parse_content(elements, el_type=None):
    parsed_elements = []
    parsed_posts = []
    parsed_comments = []
    rlink = "https://www.reddit.com"
    return_format = lambda title, link: f"{title}\n{link}\n"

    i = 0
    for element in elements:
        print(f"Working with element: {i}")
        if type(element) == Submission:
            post = reddit.submission(element)
            title = post.title
            link = rlink + post.permalink

            parsed_posts.append(return_format(title, link))
            parsed_elements.append(return_format(title, link))
        else:
            comment = reddit.comment(element)
            title = comment.body[0:70] if len(comment.body) > 71 else comment.body
            link = rlink + comment.permalink
            parsed_comments.append(return_format(title, link))
            parsed_elements.append(return_format(title, link))
        i += 1

    if el_type == "post":
        return parsed_posts
    elif el_type == "comments":
        return parsed_comments
    else:
        return parsed_elements


def get_all(elements):
    for element in parse_content(elements):
        print(element)


def get_self(posts):
    self_posts = []
    for post in posts:
        if reddit.submission(post).selftext:
            self_posts.append(post)
    self_posts = parse_content(self_posts, el_type="post")

    for post in self_posts:
        print(post)


def get_nsfw(elements):
    nsfw = []
    for element in elements:
        if reddit.submission(element).over_18:
            nsfw.append(element)
    nsfw = parse_content(nsfw, el_type="posts")
    for post in nsfw:
        print(post)


def get_subreddit(elements, subreddit):
    matched_subreddit = []

    for element in elements:
        if type(element) == Submission:
            if str(reddit.submission(element).subreddit).lower() in subreddit:
                matched_subreddit.append(element)
        else:
            if reddit.comment(element).subreddit == subreddit:
                matched_subreddit.append(element)
    matched_subreddit = parse_content(matched_subreddit)

    for item in matched_subreddit:
        print(item)


def get_media(posts, media_type="all"):
    """Get media, it can be video, gif or img"""
    if media_type == "img":
        # TODO: This also matches imgur gifs
        pattern = "i.redd.it\/.+\.jpg|imgur.com"
    elif media_type == "gif":
        # i.imgur.com/[ANYTHING].gifv
        # i.redd.it/[ANYTHING].gif
        pattern = "i.redd.it\/.+\.gif|i.imgur\.com\/.+\.gifv|gfycat"
    elif media_type == "vid":
        pattern = "pornhub.com|v\.redd\.it|youtube.com"
    else:
        pattern = ".+"

    matched_posts = []

    for post in posts:
        if re.search(pattern, post.url):
            matched_posts.append(post)
    matched_posts = parse_content(matched_posts)

    for matched_post in matched_posts:
        print(matched_post)


if __name__ == '__main__':
    saved_all, saved_posts, saved_comments = get_saved()
    print("All posts gathered")
    #get_media(saved_posts, media_type="vid")
    t0 = time.time()
    get_subreddit(saved_all, ["wtf", "python"])
    print(t0)
