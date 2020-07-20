import os
import sys
import pathlib
import click
from filter import Filter


@click.group()
@click.pass_context
@click.option("--user")
def cli(ctx, user):
    ctx.obj = Filter(user) if user else Filter()


@cli.command()
@click.pass_obj
def show_all(ctx: Filter):
    matched = ctx.get_all()
    ctx.parse_content(matched)


@cli.command()
@click.argument('query', required=True)
@click.pass_obj
def search_post(ctx: Filter, query):
    matched = ctx.search_posts(query)
    ctx.parse_content(matched)


@cli.command()
@click.argument('query', required=True)
@click.pass_obj
def search_comment(ctx: Filter, query):
    print(query)
    matched = ctx.search_comments(query)
    ctx.parse_content(matched)


@cli.command()
@click.pass_obj
def get_nsfw(ctx: Filter):
    matched = ctx.get_nsfw()
    ctx.parse_content(matched)


@cli.command()
@click.argument('subs', nargs=-1, required=True)
@click.pass_obj
def subreddits(ctx: Filter, subs):
    matched = ctx.get_subreddit([x.lower() for x in subs])
    ctx.parse_content(matched)


@cli.command()
@click.argument('media_type', required=True)
@click.pass_obj
def media(ctx: Filter, media_type):
    matched = ctx.get_media(media_type)
    ctx.parse_content(matched)


@cli.command()
@click.pass_obj
def get_self(ctx: Filter):
    matched = ctx.get_self()
    ctx.parse_content(matched)


@cli.command()
@click.pass_obj
def get_posts(ctx: Filter):
    print("Getting posts...")
    matched = ctx.get_posts()
    ctx.parse_content(matched)


@cli.command()
@click.pass_obj
def get_comments(ctx: Filter):
    print("Getting comments...")
    matched = ctx.get_comments()
    ctx.parse_content(matched)


@cli.command()
@click.pass_obj
def get_external_links(ctx: Filter):
    print("Getting external links")
    matched = ctx.get_external_links()
    ctx.parse_content(matched)


if __name__ == '__main__':
    script_dir = pathlib.Path(__file__).parent.absolute()
    os.chdir(script_dir)

    if len(sys.argv) == 1:
        Filter().main_menu()
    else:
        cli()
