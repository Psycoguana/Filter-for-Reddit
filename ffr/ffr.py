import os
import sys
import pathlib
import click
from filter import Filter


@click.group()
@click.pass_context
@click.option("-u", "--user", help="Specify which user to use.")
def cli(ctx, user):
    ctx.obj = Filter(user) if user else Filter()


@cli.command(help="Get everything that's been saved.")
@click.pass_obj
def show_all(ctx: Filter):
    print("Getting every saved element...")
    matched = ctx.get_all()
    ctx.parse_content(matched)


@cli.command(help="Get every saved post.")
@click.pass_obj
def posts(ctx: Filter):
    print("Getting every saved post...")
    matched = ctx.get_posts()
    ctx.parse_content(matched)

@cli.command(help="Get every saved comment.")
@click.pass_obj
def comments(ctx: Filter):
    print("Getting every saved comment...")
    matched = ctx.get_comments()
    ctx.parse_content(matched)


@cli.command(help="Get every saved post that only containts text.")
@click.pass_obj
def text_only(ctx: Filter):
    print("Filtering only-text posts...")
    matched = ctx.get_self()
    ctx.parse_content(matched)


@cli.command(help="Filter posts with media by it's type [img, gif, vid].")
@click.argument('media_type', required=True, type=click.Choice(['img', 'gif', 'vid']))
@click.pass_obj
def filter_media(ctx: Filter, media_type):
    print(f"Filtering media with type: {media_type}")
    matched = ctx.get_media(media_type)
    ctx.parse_content(matched)


@cli.command(help="Filter elements from one or more subreddit.")
@click.argument('subs', nargs=-1, required=True)
@click.pass_obj
def subreddits(ctx: Filter, subs):
    print("Filtering subreddits...")
    matched = ctx.get_subreddit([x.lower() for x in subs])
    ctx.parse_content(matched)


@cli.command(help="Filter posts containing a certain word.")
@click.argument('query', required=True)
@click.pass_obj
def search_posts(ctx: Filter, query):
    print(f"Searching {query} in saved posts...")
    matched = ctx.search_posts(query)
    ctx.parse_content(matched)


@cli.command(help="Filter comments containing a certain word.")
@click.argument('query', required=True)
@click.pass_obj
def search_comments(ctx: Filter, query):
    print(f"Searching {query} in saved comments...")
    matched = ctx.search_comments(query)
    ctx.parse_content(matched)


@cli.command(help="Filter every element marked as NSFW.")
@click.pass_obj
def get_nsfw(ctx: Filter):
    print("Filtering nsfw content...")
    matched = ctx.get_nsfw()
    ctx.parse_content(matched)


@cli.command(help="Get posts with links to non-Reddit websites.")
@click.pass_obj
def external_links(ctx: Filter):
    print("Filtering posts with external links...")
    matched = ctx.get_external_links()
    ctx.parse_content(matched)


if __name__ == '__main__':
    script_dir = pathlib.Path(__file__).parent.absolute()
    os.chdir(script_dir)

    if len(sys.argv) == 1:
        Filter().main_menu()
    else:
        cli()
