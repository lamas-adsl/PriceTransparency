import os
import shutil
import sys
import zipfile
from datetime import datetime, timedelta
import configparser
from dateutil.rrule import rrule, MONTHLY, DAILY
from pyunpack import Archive

# config = configparser.ConfigParser()
# config.read("config.ini")
# location = config.get("others", "LocationToSaveZip")
BASE_PATH = r'E:\marge_folder'  # location


def months(start_month, start_year, end_month, end_year):
    start = datetime(int(start_year), int(start_month), 1)
    end = datetime(int(end_year), int(end_month), 1)
    return [(str(d.day).zfill(2) + '-' + str(d.month).zfill(2) + '-' + str(d.year)) for d in
            rrule(DAILY, dtstart=start, until=end)]


def extract_folder(path, name):
    os.chdir(path)
    os.mkdir(name[:-4])
    Archive(name).extractall(name[:-4])
    return name[:-4]


def main():
    arguments = sys.argv
    start_month = arguments[1].split('-')[0]
    start_year = arguments[1].split('-')[1]
    end_month = arguments[2].split('-')[0]
    end_year = arguments[2].split('-')[1]

    for m in months(start_month, start_year, end_month, end_year):
        DATE = m  # str((datetime.today()-timedelta(1)).strftime('%d-%m-%Y'))
        folders = list(filter(lambda x: DATE in x, os.listdir(BASE_PATH)))
        # E&E 11/12/2022
        """
         רצינו למנוע מקרה של תקיה יחידה שנמחקת (תקיה שהושלמה),
         ומקרה נוסף- שנופלת התוכנית באמצע עבודה על תאריך והתוכנית נופלת כי יש לא יכולה לעשות EXTRACT לתקיות לא ZIP
        """
        # if os.path.exists(os.path.join(BASE_PATH, DATE)):
        #     shutil.rmtree(os.path.join(BASE_PATH, DATE))
        #     folders = list(filter(lambda x: DATE in x, os.listdir(BASE_PATH)))
        """"""
        if os.path.exists(os.path.join(BASE_PATH, DATE)):
            if len(folders) > 1:
                folders_to_remove = list(filter(lambda x: 'zip' not in x , folders))
                [shutil.rmtree(os.path.join(BASE_PATH, f)) for f in folders_to_remove]
                folders = list(filter(lambda x: DATE in x, os.listdir(BASE_PATH)))
            else:
                continue
        """"""
        if len(folders) > 0:
            os.mkdir(os.path.join(BASE_PATH, DATE))
        else:
            continue
        directories = {}
        for ff in folders:
            if '.crdownload' in ff or '.html' in ff or '.htm' in ff:
                os.remove(ff)
                continue
            name = extract_folder(BASE_PATH, ff)
            ff = name
            for f in os.listdir(os.path.join(BASE_PATH, ff)):
                if f not in directories:
                    directories[f] = {}
                for n in os.listdir(os.path.join(BASE_PATH, ff, f)):
                    nn = n[:-7]
                    """
                    12/12/2022
                    לטפל במקרה שבשם הקובץ יש XML
                    """
                    ''''
                    end_name = 7
                    end_name += 8 if '.xml' in n[:end_name] else end_name
                    nn = n[:-end_name]
                    '''
                    if nn in directories[f]:
                        last_date = directories[f][nn].rpartition('-')[-1]
                        this_date = n.rpartition('-')[-1]
                        if last_date[:-3] < this_date[:-3]:
                            directories[f][nn] = os.path.join(BASE_PATH, ff, f, n)
                        else:
                            continue
                    else:
                        directories[f][nn] = os.path.join(BASE_PATH, ff, f, n)
        for na in directories.keys():
            os.mkdir(os.path.join(BASE_PATH, DATE, na))
            for c in directories[na]:
                try:
                    shutil.copy(directories[na][c], os.path.join(BASE_PATH, DATE, na))
                except:
                    shutil.copy2(directories[na][c], os.path.join(BASE_PATH, DATE, na))

        for ff in folders:
            shutil.rmtree(os.path.join(BASE_PATH, ff[:-4]))
	    wrong_files = glob(rf'{BASE_PATH}/*/*/*.crdownload')
	    for w in wrong_files:
	        os.remove(w)
        shutil.make_archive(os.path.join(BASE_PATH, DATE+'_00-00-00'), 'zip', os.path.join(BASE_PATH, DATE))
        shutil.rmtree(os.path.join(BASE_PATH, DATE))

        for zipped_file in folders:
            try:
                os.remove(os.path.join(BASE_PATH, zipped_file))
            except:
                print("failed to delete: " + zipped_file)


if __name__ == "__main__":
    main()
