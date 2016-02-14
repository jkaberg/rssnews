import os
import time
import feedparser
import parsedatetime
import gevent.monkey
from gevent.pool import Pool
from datetime import datetime
from time import mktime

from flask import Flask, render_template

app = Flask(__name__)
gevent.monkey.patch_all()

update_time_sec = 60*5  # 5 min
tmp_file = "{0}/cache.tmp".format(os.path.dirname(os.path.realpath(__file__)))

if not os.path.isfile(tmp_file):
    os.mknod(tmp_file)


def fetch_feeds(urls):
    pool = Pool(10)
    feedparser._HTMLSanitizer.acceptable_elements = (['a'])  # We don't want anything else
    entries = []

    def get(url):
        parsed = feedparser.parse(url)
        if parsed.entries:
            entries.extend(parsed.entries)

    for url in urls:
        pool.spawn(get, url)
    pool.join()

    return entries


def update_cache(tmp_file, cache):
    with open(tmp_file, 'w') as file:
        file.write(str(cache))


def return_cache(tmp_file, update_time_sec):
    if os.path.getctime(tmp_file) < (time.time() - update_time_sec):
        with open(tmp_file, "r") as data:
                return data
    return None

@app.template_filter('fixtime')
def fixtime(date):
    t = parsedatetime.Calendar()
    time_struct, parse_status = t.parse(date)
    return datetime.fromtimestamp(mktime(time_struct)).strftime('%H:%M')


@app.route('/')
def index():
    entries_sorted = None #return_cache(tmp_file, update_time_sec)

    if entries_sorted is not None:
        return render_template('index.html', entries=entries_sorted)
    else:
        urls = [
            'https://lobste.rs/rss.rss',
            'http://hnrss.org/newest',
            'http://feeds.dzone.com/cloud',
            'http://feeds.dzone.com/devops',
            'http://highscalability.com/rss.xml',
            'http://www.everythingsysadmin.com/atom.xml',
            'http://feeds.techdirt.com/techdirt/feed',
            'http://xkcd.com/rss.xml',
            'http://feeds.feedburner.com/CoolTools',
            'http://www.thinkgeek.com/thinkgeek.rss'
            ]

        entries = fetch_feeds(urls)
        entries_sorted = sorted(entries, key=lambda e: e.published_parsed, reverse=True)
        update_cache(tmp_file, entries_sorted)

        return render_template('index.html', entries=entries_sorted)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
