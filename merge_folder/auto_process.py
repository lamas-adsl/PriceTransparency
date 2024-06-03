import glob
import shutil
from datetime import datetime
from sys import argv
import marge_folder_pyto as mrg
import sort_chains


def run(date):
    path = f'E:\PriceOutPut\*{date}*'
    folders = glob.glob(path)
    sort_chains.run(path)
    mrg.run(path, date)


if __name__ == "__main__":
    try:
        date = argv[1]
    except:
        date = (datetime.now() - datetime.timedelta(days=1)).strftime('%d-%m-%Y')
    run(date)
