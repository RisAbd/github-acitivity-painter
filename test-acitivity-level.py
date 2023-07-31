
import optparse

import os, subprocess
from pathlib import Path
import datetime as dt


def main():

    opt_parser = optparse.OptionParser()

    opts, args = opt_parser.parse_args()

    git_dir = Path(next(iter(args), '.'))
    assert git_dir.is_dir() or not git_dir.exists()

    if not git_dir.exists():
        git_dir.mkdir()

    os.chdir(git_dir)

    dummy_file = Path('file.dummy')

    start_date = dt.date(2023, 6, 18)
    end_date = start_date + dt.timedelta(days=7) #dt.date(2023, 7, 29)

    os.system(f'''
git init
git config commit.gpgsign false''')

    assert end_date > start_date

    def iter_days():
        date = start_date
        while date <= end_date:
            yield date
            date += dt.timedelta(days=1)

    for i, date in enumerate(iter_days()):
        date_s = date.strftime('%Y-%m-%dT00:00:00')

        print(date_s)
        for j in range(i+1):
            with dummy_file.open('a') as fp:
                fp.write(f'{i}.{j}\n')

            p = subprocess.run(f'''
git add {dummy_file}
git commit -m 'kek `{i}.{j}`' ''', 
                shell=True,
                env=dict(os.environ, 
                         GIT_AUTHOR_DATE=date_s, 
                         GIT_COMMITTER_DATE=date_s)
            )
        print(f'committed {i+1} commits...')

    print('Finished.')


if __name__ == '__main__':
    main()






