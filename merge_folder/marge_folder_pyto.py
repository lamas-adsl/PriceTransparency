import os
import shutil
import time
from datetime import datetime
import configparser
from glob import glob
from dateutil.rrule import rrule, DAILY
from pyunpack import Archive

config = configparser.ConfigParser()
config.read("config.ini")
location = f'E:/marge_folder/'


def extract_folder(path, name):
    os.chdir(path)
    os.mkdir(name[:-4])
    Archive(name).extractall(name[:-4])
    return name[:-4]


def run(path, DATE):
    folders = glob(f'{path}.zip')
    """
     רצינו למנוע מקרה של תקיה יחידה שנמחקת (תקיה שהושלמה),
     ומקרה נוסף- שנופלת התוכנית באמצע עבודה על תאריך והתוכנית נופלת כי יש לא יכולה לעשות EXTRACT לתקיות לא ZIP
    """
    if os.path.exists(f'{location}/{DATE}'):
        shutil.rmtree(f'{location}/{DATE}')
    if len(folders) > 0:
        os.mkdir(f'{location}/{DATE}')
    else:
        return

    directories = {}
    for ff in folders:
        folder_name = ff.split('\\')[-1]
        shutil.copy(ff, f'{location}/{DATE}/{folder_name}')
        ff = extract_folder(f'{location}/{DATE}', folder_name)
        for f in os.listdir(os.path.join(ff)):
            if f not in directories:
                directories[f] = {}
            if f.endswith('chromedriver.exe'):
                os.remove(f)
                continue
            for n in os.listdir(os.path.join(ff, f)):
                if n == 'downloads.htm':
                    os.remove(os.path.join(ff, f, n))
                    continue
                if n.split('.')[-1] == 'xml':
                    nn = n[:-8]
                else:
                    nn = n[:-7]
                if len(nn.split('-')[-1]) == 3:
                    nn = nn[:-8]

                if nn.split('-')[-1] != datetime.strptime(DATE, '%d-%m-%Y').strftime('%Y%m%d'):
                    continue
                if nn in directories[f]:
                    last_date = directories[f][nn].rpartition('-')[-1][:-3]
                    this_date = n.rpartition('-')[-1][:-3]
                    if last_date < this_date:
                        directories[f][nn] = os.path.join( ff, f, n)
                    else:
                        continue
                else:
                    directories[f][nn] = os.path.join(ff, f, n)
    for na in directories.keys():
        os.mkdir(f'{location}/{DATE}/{na}')
        for c in directories[na]:
            try:
                shutil.copy(directories[na][c], f'{location}/{DATE}/{na}')
            except:
                shutil.copy2(directories[na][c], f'{location}/{DATE}/{na}')
    time.sleep(10)
    for ff in folders:
        folder_name = ff.split('\\')[-1]
        shutil.rmtree(f'{location}/{DATE}/{folder_name[:-4]}')
        os.remove(f'{location}/{DATE}/{folder_name}')
    wrong_files = glob(rf'{location}/*/*/*.crdownload')
    for w in wrong_files:
        os.remove(w)
    shutil.make_archive(os.path.join(location, DATE+'_00-00-00'), 'zip', os.path.join(f'{location}', DATE))
    try:
        shutil.rmtree(os.path.join(f'{location}', DATE))
    except:
        pass

    for zipped_file in folders:
        try:
            os.remove(os.path.join(location, zipped_file))
        except:
            print("failed to delete: " + zipped_file)
    shutil.copy(f'{location}/{DATE}_00-00-00.zip', f'E:/PriceOutPutForFtp')


if __name__ == "__main__":
    run('13-05-2023')
