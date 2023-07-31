
import os, subprocess, shutil

import requests
from bs4 import BeautifulSoup

from requests_cache import CachedSession

import itertools as IT, functools as FT, operator as OP

import datetime as dt

from pprint import pprint
from pathlib import Path
import typing as T



def date_to_nearest_saturday(date):
    while date.weekday() != 5:
        date -= dt.timedelta(days=1)
    return date


# def transform_commitmap(p: Path) -> T.List[(dt.datetime, )]


def main():

    # GET CURRENT ACTIVITY MAP

    session = CachedSession('requests_cache')
    r = session.get('https://github.com/RisAbd')
    r.raise_for_status()

    soup = BeautifulSoup(r.content, 'html.parser')

    # table = soup.find('table', class_='ContributionCalendar-grid')

    # breakpoint()

    activity_tbody = soup.find('table', class_='ContributionCalendar-grid').tbody

    activity = dict()
    for td in activity_tbody.find_all('td', class_='ContributionCalendar-day'):
        date = dt.datetime.strptime(td.attrs['data-date'], '%Y-%m-%d').date()
        level = int(td.attrs['data-level'])
        contribs = int(c) if (c := td.span.get_text().split()[0]) != 'No' else 0
        activity[date] = dict(level=level, contribs=contribs)

    activity = dict(sorted(activity.items()))

    pprint({k: v for k, v in activity.items() if v['level'] > 0}) 
    min_date = min(activity.keys())  # first date is Sun in activity
    max_date = max(activity.keys())
    max_date = date_to_nearest_saturday(max_date)  # last date is last Sat

    max_commits_count = max(map(OP.itemgetter('contribs'), activity.values()))
    block_size = (max_commits_count + (4 - (max_commits_count % 4))) // 4

    print(min_date, max_date)

    activity_matrix = []
    r = None
    for i, (date, info) in enumerate(activity.items()):
        if i % 7 == 0:
            r = []
            activity_matrix.append(r)
        r.append(info['level'])
    while len(r) < 7:
        r.append(0)

    for i in range(7):
        print(''.join(map(str, map(OP.itemgetter(i), activity_matrix))))

    # GET NEW ACTIVITY MAP

    commitmap_file = Path('moto.commitmap')
    print()
    print(commitmap_file.read_text())

    s = commitmap_file.read_text()
    s = [list(map(int, l)) for l in s.split('\n')]

    def iter_commitmap_data():
        date = min_date
        for i in range(len(s[0])):
            for j in range(len(s)):
                level = s[j][i]
                if level > 0:
                    yield (date, level * block_size)
                date += dt.timedelta(days=1)

    # print(*list(iter_commitmap_data()), sep='\n')

    # CREATE REPO WITH NEW COMMITS

    git_dir = Path('kek/')

    if git_dir.exists():
        shutil.rmtree(git_dir)
    git_dir.mkdir()

    prev_cwd = Path(os.getcwd())

    os.chdir(git_dir)

    dummy_file = Path('file.dummy')

    os.system(f'''
git init
git config commit.gpgsign false''')

    for date, commits_count in iter_commitmap_data():
        date_s = date.strftime('%Y-%m-%dT00:00:00')
        print(date_s)

        current_user_contribs_count = activity[date]['contribs'] 

        for i in range(max(0, commits_count-current_user_contribs_count)):
            with dummy_file.open('a') as fp:
                fp.write(f'{date} {i}\n')

            p = subprocess.run(f'''
git add {dummy_file}
git commit -m 'kek `{date}.{i}`' ''', 
                shell=True,
                env=dict(os.environ, 
                         GIT_AUTHOR_DATE=date_s, 
                         GIT_COMMITTER_DATE=date_s)
            )
        print(f'committed {i+1} commits...')

    os.chdir(prev_cwd)



if __name__ == '__main__':
    main()
