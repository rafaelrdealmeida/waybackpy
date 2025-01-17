from waybackpy.utils import latest_version, DEFAULT_USER_AGENT
from waybackpy.__version__ import __version__


def test_default_user_agent():
    assert (
        DEFAULT_USER_AGENT
        == "waybackpy %s - https://github.com/akamhy/waybackpy" % __version__
    )


def test_latest_version():
    assert __version__ == latest_version(package_name="waybackpy")
