"""Console script for nature_polymerase."""
import sys
import click
from nature_polymerase import nature_polymerase


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--url', default=None)
@click.option('--use_proxy', default=True)
def main(url=None, use_proxy=True):
    """Console script for nature_polymerase."""
    if url is not None:
        nature_polymerase.save_journal_issue(url)
    elif use_proxy:
        nature_polymerase.get_fresh_issues_proxy()
    else:
        nature_polymerase.get_fresh_issues()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
