"""Console script for paperstitch."""
import sys
import click
from paperstitch import paperstitch

@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--url',default=None)
def main(url=None):
    """Console script for paperstitch."""
    if url is not None:
        paperstitch.save_journal_issue(url)
    else:
        # paperstitch.get_fresh_issues()
        paperstitch.get_fresh_issues_proxy()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
