import pytest
import time
import random
import string
from datetime import datetime

from waybackpy.save_api import WaybackMachineSaveAPI
from waybackpy.exceptions import MaximumSaveRetriesExceeded

rndstr = lambda n: "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(n)
)


def test_save():
    url = "https://github.com/akamhy/waybackpy"
    user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    save_api.save()
    archive_url = save_api.archive_url
    timestamp = save_api.timestamp()
    headers = save_api.headers  # CaseInsensitiveDict
    cached_save = save_api.cached_save
    assert cached_save in [True, False]
    assert archive_url.find("github.com/akamhy/waybackpy") != -1
    assert str(headers).find("github.com/akamhy/waybackpy") != -1
    assert type(save_api.timestamp()) == type(datetime(year=2020, month=10, day=2))


def test_max_redirect_exceeded():
    with pytest.raises(MaximumSaveRetriesExceeded):
        url = "https://%s.gov" % rndstr
        user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
        save_api = WaybackMachineSaveAPI(url, user_agent, max_tries=3)
        save_api.save()


def test_sleep():
    """
    sleeping is actually very important for SaveAPI
    interface stability.
    The test checks that the time taken by sleep method
    is as intended.
    """
    url = "https://example.com"
    user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    s_time = int(time.time())
    save_api.sleep(6)  # multiple of 3 sleep for 10 seconds
    e_time = int(time.time())
    assert (e_time - s_time) >= 10

    s_time = int(time.time())
    save_api.sleep(7)  # sleeps for 5 seconds
    e_time = int(time.time())
    assert (e_time - s_time) >= 5


def test_timestamp():
    url = "https://example.com"
    user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    now = datetime.utcnow()
    save_api._archive_url = (
        "https://web.archive.org/web/%s/" % now.strftime("%Y%m%d%H%M%S") + url
    )
    save_api.timestamp()
    assert save_api.cached_save is False
    save_api._archive_url = "https://web.archive.org/web/%s/" % "20100124063622" + url
    save_api.timestamp()
    assert save_api.cached_save is True


def test_archive_url_parser():
    """
    Testing three regex for matches and also tests the response URL.
    """
    url = "https://example.com"
    user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
    save_api = WaybackMachineSaveAPI(url, user_agent)

    save_api.headers = """
    START
    Content-Location: /web/20201126185327/https://www.scribbr.com/citing-sources/et-al
    END
    """

    assert (
        save_api.archive_url_parser()
        == "https://web.archive.org/web/20201126185327/https://www.scribbr.com/citing-sources/et-al"
    )

    save_api.headers = """
    {'Server': 'nginx/1.15.8', 'Date': 'Sat, 02 Jan 2021 09:40:25 GMT', 'Content-Type': 'text/html; charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'X-Archive-Orig-Server': 'nginx', 'X-Archive-Orig-Date': 'Sat, 02 Jan 2021 09:40:09 GMT', 'X-Archive-Orig-Transfer-Encoding': 'chunked', 'X-Archive-Orig-Connection': 'keep-alive', 'X-Archive-Orig-Vary': 'Accept-Encoding', 'X-Archive-Orig-Last-Modified': 'Fri, 01 Jan 2021 12:19:00 GMT', 'X-Archive-Orig-Strict-Transport-Security': 'max-age=31536000, max-age=0;', 'X-Archive-Guessed-Content-Type': 'text/html', 'X-Archive-Guessed-Charset': 'utf-8', 'Memento-Datetime': 'Sat, 02 Jan 2021 09:40:09 GMT', 'Link': '<https://www.scribbr.com/citing-sources/et-al/>; rel="original", <https://web.archive.org/web/timemap/link/https://www.scribbr.com/citing-sources/et-al/>; rel="timemap"; type="application/link-format", <https://web.archive.org/web/https://www.scribbr.com/citing-sources/et-al/>; rel="timegate", <https://web.archive.org/web/20200601082911/https://www.scribbr.com/citing-sources/et-al/>; rel="first memento"; datetime="Mon, 01 Jun 2020 08:29:11 GMT", <https://web.archive.org/web/20201126185327/https://www.scribbr.com/citing-sources/et-al/>; rel="prev memento"; datetime="Thu, 26 Nov 2020 18:53:27 GMT", <https://web.archive.org/web/20210102094009/https://www.scribbr.com/citing-sources/et-al/>; rel="memento"; datetime="Sat, 02 Jan 2021 09:40:09 GMT", <https://web.archive.org/web/20210102094009/https://www.scribbr.com/citing-sources/et-al/>; rel="last memento"; datetime="Sat, 02 Jan 2021 09:40:09 GMT"', 'Content-Security-Policy': "default-src 'self' 'unsafe-eval' 'unsafe-inline' data: blob: archive.org web.archive.org analytics.archive.org pragma.archivelab.org", 'X-Archive-Src': 'spn2-20210102092956-wwwb-spn20.us.archive.org-8001.warc.gz', 'Server-Timing': 'captures_list;dur=112.646325, exclusion.robots;dur=0.172010, exclusion.robots.policy;dur=0.158205, RedisCDXSource;dur=2.205932, esindex;dur=0.014647, LoadShardBlock;dur=82.205012, PetaboxLoader3.datanode;dur=70.750239, CDXLines.iter;dur=24.306278, load_resource;dur=26.520179', 'X-App-Server': 'wwwb-app200', 'X-ts': '200', 'X-location': 'All', 'X-Cache-Key': 'httpsweb.archive.org/web/20210102094009/https://www.scribbr.com/citing-sources/et-al/IN', 'X-RL': '0', 'X-Page-Cache': 'MISS', 'X-Archive-Screenname': '0', 'Content-Encoding': 'gzip'}
    """

    assert (
        save_api.archive_url_parser()
        == "https://web.archive.org/web/20210102094009/https://www.scribbr.com/citing-sources/et-al/"
    )

    save_api.headers = """
    START
    X-Cache-Key: https://web.archive.org/web/20171128185327/https://www.scribbr.com/citing-sources/et-al/US
    END
    """

    assert (
        save_api.archive_url_parser()
        == "https://web.archive.org/web/20171128185327/https://www.scribbr.com/citing-sources/et-al/"
    )

    save_api.headers = "TEST TEST TEST AND NO MATCH - TEST FOR RESPONSE URL MATCHING"
    save_api.response_url = "https://web.archive.org/web/20171128185327/https://www.scribbr.com/citing-sources/et-al"
    assert (
        save_api.archive_url_parser()
        == "https://web.archive.org/web/20171128185327/https://www.scribbr.com/citing-sources/et-al"
    )


def test_archive_url():
    """
    Checks the attribute archive_url's value when the save method was not
    explicitly invoked by the end-user but the save method was invoked implicitly
    by the archive_url method which is an attribute due to @property.
    """
    url = "https://example.com"
    user_agent = "Mozilla/5.0 (MacBook Air; M1 Mac OS X 11_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/604.1"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    save_api.saved_archive = (
        "https://web.archive.org/web/20220124063056/https://example.com/"
    )
    assert save_api.archive_url == save_api.saved_archive
