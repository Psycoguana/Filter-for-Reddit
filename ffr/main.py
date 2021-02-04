import click

try:
    from ffr.filter import Filter
    from ffr.login import is_new_user, login as auth
except ModuleNotFoundError:
    from filter import Filter
    from login import is_new_user, login as auth

from version import __version__



@click.group(invoke_without_command=True)
@click.version_option(prog_name="Filter for Reddit", version=__version__)
@click.pass_context
@click.option("-l", "--limit", type=int, help="Specify the maximum amount of elements to retrieve")
@click.option("-u", "--user", help="Specify which user to use.")
def cli(ctx, user, limit):
    if is_new_user():
        print("You can't filter any post until you log in. Don't worry, it's only the first time :)\n")
        auth()
    elif ctx.invoked_subcommand is None:
        Filter(async_mode=True).main_menu()
    elif ctx.invoked_subcommand == 'login':
        # Does not create the Filter object when login, cause there's no credentials that can be used.
        pass
    elif user and limit:
        ctx.obj = Filter(user, limit)
    elif user:
        ctx.obj = Filter(user=user)
    elif limit:
        ctx.obj = Filter(limit=limit)
    else:
        ctx.obj = Filter()


@cli.command(help="Get everything that's been saved.")
@click.pass_obj
def show_all(ctx: Filter):
    matched = ctx.get_all()
    ctx.parse_content(matched)


@cli.command(help="Get every saved post.")
@click.pass_obj
def posts(ctx: Filter):
    matched = ctx.get_posts()
    ctx.parse_content(matched)


@cli.command(help="Get every saved comment.")
@click.pass_obj
def comments(ctx: Filter):
    matched = ctx.get_comments()
    ctx.parse_content(matched)


@cli.command(help="Get every saved post that only contains text.")
@click.pass_obj
def text_only(ctx: Filter):
    matched = ctx.get_self()
    ctx.parse_content(matched)


@cli.command(help="Filter posts with media by it's type [img, gif, vid].")
@click.argument('media_type', required=True, type=click.Choice(['img', 'gif', 'vid']))
@click.pass_obj
def filter_media(ctx: Filter, media_type):
    matched = ctx.get_media(media_type)
    ctx.parse_content(matched)


@cli.command(help="Filter elements from one or more subreddit.")
@click.argument('subs', nargs=-1, required=True)
@click.pass_obj
def subreddits(ctx: Filter, subs):
    matched = ctx.get_subreddit([x.lower() for x in subs])
    ctx.parse_content(matched)


@cli.command(help="Filter posts containing a certain word.")
@click.argument('query', required=True)
@click.pass_obj
def search_posts(ctx: Filter, query):
    matched = ctx.search_posts(query)
    ctx.parse_content(matched)


@cli.command(help="Filter comments containing a certain word.")
@click.argument('query', required=True)
@click.pass_obj
def search_comments(ctx: Filter, query):
    matched = ctx.search_comments(query)
    ctx.parse_content(matched)


@cli.command(help="Filter every element marked as NSFW.")
@click.pass_obj
def get_nsfw(ctx: Filter):
    matched = ctx.get_nsfw()
    ctx.parse_content(matched)


@cli.command(help="Get posts with links to non-Reddit websites.")
@click.pass_obj
def external_links(ctx: Filter):
    matched = ctx.get_external_links()
    ctx.parse_content(matched)


@cli.command(help="Create Reddit credentials.")
def login():
    auth()


if __name__ == '__main__':
    cli()
