import os
import sys


def get_version():
    """
    Return the formatted version information
    """
    vers = ['%(major)i.%(minor)i' % __version_info__, ]

    if __version_info__['micro']:
        vers.append('.%(micro)i' % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)


__version_info__ = {
    'major': 0,
    'minor': 9,
    'micro': 0,
    'releaselevel': 'alpha',
    'serial': 0
}
__version__ = get_version()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(PROJECT_ROOT, '3rd_party'))
