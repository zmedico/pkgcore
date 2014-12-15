# Copyright: 2015 Tim Harder <radhermit@gmail.com
# License: BSD/GPL2

"""Display keywords for specified targets."""

import argparse

from pkgcore.util import commandline
from pkgcore.util import parserestrict


class StoreTarget(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, basestring):
            values = [values]
        for x in values:
            argparse._AppendAction.__call__(
                self, parser, namespace,
                (x, parserestrict.parse_match(x)), option_string=option_string)


argparser = commandline.mk_argparser(description=__doc__)

argparser.add_argument(
    "--no-filters", action='store_true', default=False,
    help="With this option enabled, all license filtering, visibility filtering"
         " (ACCEPT_KEYWORDS, package masking, etc) is turned off.")
argparser.add_argument(
    'targets', nargs='+', action=StoreTarget,
    help="extended atom matching of packages")

argparser.add_argument(
    '-r', '--repo',
    action=commandline.StoreRepoObject, priority=29,
    help='repo to use (default from domain if omitted).')


@argparser.bind_delayed_default(30, 'repos')
def setup_repos(namespace, attr):
    # Get repo(s) to operate on.
    if namespace.repo:
        repos = [namespace.repo]
    else:
        repos = namespace.domain.repos_configured.itervalues()

    setattr(namespace, attr, repos)


@argparser.bind_main_func
def main(options, out, err):
    for token, restriction in options.targets:
        pkgs = []
        for repo in options.repos:
            pkgs += repo.match(restriction)

        if not pkgs:
            err.write("no matches for '%s'" % (token,))
            return 1

        for pkg in pkgs:
            out.write('%s: %s' % (pkg.cpvstr, ', '.join(pkg.keywords)))
