import glob
import os
import shutil
from time import sleep
import pandas as pd
from pyunpack import Archive
import rename_gbrash

chains = {'ויקטורי רשת סופרמרקטים בעמ': '7290696200003',
          'ח  כהן סוכנות מזון ומשקאות בעמ': '7290455000004',
          'כ נ מחסני השוק בעמ_A': '7290633800006',
          'כ נ מחסני השוק בעמ_B':'7290661400001',
          '(יינות ביתן בעמ) גלובל ריטייל בעמ (קרפור , מגה בעיר , יינות ביתן, שותפות אונליין )_A': '7290725900003',
          '(יינות ביתן בעמ) גלובל ריטייל בעמ (קרפור , מגה בעיר , יינות ביתן, שותפות אונליין )_B': '7290055700007',
          '(יינות ביתן בעמ) גלובל ריטייל בעמ (קרפור , מגה בעיר , יינות ביתן, שותפות אונליין )_C': '7291029710008',
          'פז חברת נפט בעמ_A':'7290644700005',
          'פז חברת נפט בעמ_B': '7290058177776',
          'רשת חנויות רמי לוי שיווק השקמה 2006 בעמ(כולל רשת סופר קופיקס)_A':'7290058140886',
          'רשת חנויות רמי לוי שיווק השקמה 2006 בעמ(כולל רשת סופר קופיקס)_B':'7291056200008'
          }


def fill_chain():
    df = pd.read_csv(r'D:\Price_Transparency\markets_list.csv', encoding="iso8859_8")
    for i in df.iterrows():
        f_name = i[1]['שם'].replace('xa0\\', ' ').replace(' ', ' ').replace('\\xa0', ' ').replace('"', '').replace('.', ' ')
        while str(f_name).endswith(' '):
            f_name = f_name[:-1]
        while str(f_name)[-1] == ' ':
            f_name = f_name[:-1]
        if f_name not in chains:
            if f_name[-2] == '_':
                if f_name[:-2]+'_A' in chains:
                    continue
            else:
                if f_name+'_A' in chains:
                    continue
            if f_name not in chains:
                if len(str(i[1]['URL']).split(',')) > 1:
                    ind = 0
                    for u in str(i[1]['URL']).split(','):
                        chains[f"{str(f_name).strip()}_{chr(ord('A') + ind)}"] = ''
                        ind += 1
                else:
                    chains[f_name] = ''


def extract_folder(path, name):
    os.chdir(path)
    os.mkdir(name[:-4])
    Archive(name).extractall(name[:-4])
    return name[:-4]


def run(path= r'D:\adsl_data\02_04_2024-07_53_48'):
    fill_chain()
    for i in glob.glob(fr'{path}*.zip'):
        name = extract_folder(i[:len(i)-(len(i.split('\\')[-1])+1)], i.split('\\')[-1])
        i = i.replace('.zip', '')
        os.mkdir(fr'{i}\temp_sort')
        for n in glob.glob(f'{i}\*'):
            gbrash = n.split('\\')[-1]
            nn = n.split('\\')[-1].replace(' ', ' ')
            if nn in rename_gbrash.names.keys():
                running = True
                c = ''
                ide = 0
                while(running):
                    try:
                        os.rename(n, f'{n.replace(gbrash, rename_gbrash.names[nn])}{c}')
                        running = False
                    except:
                        ide = ide + 1
                        c = f'_{ide}'
        for value in chains:
            if chains[value] == '':
                if str(value).endswith('A') or str(value).endswith('B') or str(value).endswith('C'):
                    try:
                        if (glob.glob(f'{i}\{value[:-2]}*\PriceF*'))[0]:
                            chain = (glob.glob(f'{i}\{value[:-2]}*\PriceF*'))[0].split('\\')[-1][9:21]
                    except:
                        continue
                else:
                    try:
                        if (glob.glob(f'{i}\{value}\PriceF*'))[0]:
                            chain = (glob.glob(f'{i}\{value}\PriceF*'))[0].split('\\')[-1][9:21]
                    except:
                        continue
            else:
                chain = chains[value]
            if len(str(chain).split(',')) > 1:
                files= []
                for v in str(chain).split(','):
                    files += glob.glob(f'{i}\*\*{v}*')
            else:
                files = glob.glob(f'{i}\*\*{chain}*')
            for f in files:
                try:
                    shutil.move(f, rf'{i}\temp_sort')
                    name_dir = f.split("\\")[-1]
                    if not os.path.exists(rf'{i}\{value}'):
                        os.mkdir(rf'{i}\{value}')
                    shutil.move(rf'{i}\temp_sort\{name_dir}', rf'{i}\{value}')
                except Exception as e:
                    continue
        for ff in glob.glob(f'{i}\*'):
            if ff.endswith('chromedriver.exe'):
                os.remove(ff)
                continue
            elif not os.listdir(ff) or (len(os.listdir(ff))==1 and os.listdir(ff)[0] == 'downloads.htm') :
                shutil.rmtree(ff)
                continue
        for ff in glob.glob(f'{i}\*_[1-9]'):
            try:
                os.rename(ff, ff[:-2])
            except:
                pass
        try:
            shutil.rmtree(rf'{i}\temp_sort')
        except:
            pass
        shutil.make_archive(f'{i}', 'zip', f'{i}')
        sleep(5)
        shutil.rmtree(rf'{i}')