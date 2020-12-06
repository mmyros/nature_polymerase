"""Console script for paperstitch."""
import sys
import click
from paperstitch import paperstitch


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--url', default=None)
@click.option('--use_proxy', default=True)
def main(url=None, use_proxy=True):
    """Console script for paperstitch."""
    if url is not None:
        paperstitch.save_journal_issue(url)
    elif use_proxy:
        paperstitch.get_fresh_issues_proxy()
    else:
        paperstitch.get_fresh_issues()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
