import os
import sys

from PyQt5.QtWidgets import QApplication
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager
from itertools import repeat
import multiprocessing
import traceback
import pandas as pd

import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException

from common import browser
from common import guiWindow

__author__ = 'Yeonghun Lee <lyhgod@gmail.com>'


def crawling(pool_id, pool_path, pool_url, pool_dict):
    final_result_dict = {}

    chrome_control = browser.ChromeControl(pool_path.value)
    chrome_control.driver.get(pool_url.value + 'summoner/userName=' + pool_id)

    # 솔로 랭크 버튼 클릭
    try:
        chrome_control.button_click('//*[@id="__next"]/div[5]/div[2]/div[1]/ul/li[2]/button')
    except NoSuchElementException:
        final_result_dict['전적'] = '없음'
    else:
        solo_game_list = chrome_control.find_elements('//*[@id="__next"]/div[5]/div[2]/ul/li')
        if len(solo_game_list) == 0:
            final_result_dict['전적'] = '없음'
        else:
            # 전적 ex) 20전 13승 7 패
            total_win_lose = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[1]/td[1]')
            final_result_dict['전적'] = total_win_lose

            # 승률 ex) 53%
            win_rate = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[2]/td[1]/div/div[2]')
            final_result_dict['승률'] = win_rate

            # kda ex) 2.27:1
            kda = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[2]/td[2]/div[2]/span')
            final_result_dict['K/D/A'] = kda[:-2]

            # 킬 관여율 ex) (47%)
            kill_relate = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[2]/td[2]/div[2]/div/span')
            final_result_dict['킬 관여율'] = kill_relate

            # 모스트 챔프
            most_champ = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[1]/td[2]/ul')
            final_result_dict['모스트 챔프'] = most_champ.split('\n')[0]

            # 모스트 라인
            most_line = chrome_control.get_text('//*[@id="__next"]/div[5]/div[2]/div[2]/table/tbody/tr[2]/td[3]/ul')
            final_result_dict['모스트 라인'] = most_line.split('\n')[0]

            total_rank_point = 0
            for i in range(1, len(solo_game_list) + 1):
                # detail 태그는 접혀져 있어서 selenium 으로 펼치기 해줘야 함
                check_record = chrome_control.find_elements('//*[@id="__next"]/div[5]/div[2]/ul/li[' + str(i) + ']/div/div[7]/button')
                if len(check_record) == 1:
                    chrome_control.button_click('//*[@id="__next"]/div[5]/div[2]/ul/li[' + str(i) + ']/div/div[7]/button/img')
                # 녹화 버튼 있을 경우
                elif len(check_record) == 2:
                    chrome_control.button_click('//*[@id="__next"]/div[5]/div[2]/ul/li[' + str(i) + ']/div/div[7]/button[2]/img')

                table = chrome_control.find_element('//*[@id="__next"]/div[5]/div[2]/ul/li[' + str(i) + ']/div[2]/div/table[1]').get_attribute('outerHTML')
                soup = BeautifulSoup(table, 'html.parser')
                df = pd.read_html(str(soup), header=0, encoding='utf-8')[0]

                if str(df['OP Score'][0]) == 'nan':
                    # 다시하기
                    pass
                else:
                    rank_list = {}
                    for j in range(0, 5):
                        if (df['OP Score'][j][4:5] == 'A') or (df['OP Score'][j][4:5] == 'M'):
                            rank_list[df[df.columns[3]][j]] = 1
                        elif df['OP Score'][j][4:5] == '0':
                            rank_list[df[df.columns[3]][j]] = 1
                        elif df['OP Score'][j][4:5] == '1':
                            rank_list[df[df.columns[3]][j]] = 10
                        else:
                            rank_list[df[df.columns[3]][j]] = int(df['OP Score'][j][4:5])
                    rank_list_key = sorted(rank_list, key=lambda x: rank_list[x])
                    rank_value = rank_list_key.index(pool_id) + 1
                    total_rank_point += rank_value
            average_rank = total_rank_point / len(solo_game_list)
            final_result_dict['팀내 평균 등수'] = str(round(average_rank))

    pool_dict[pool_id] = final_result_dict
    chrome_control.driver.quit()


def version_check(version):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get('https://github.com/20hun/lolscouter', headers=headers)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # 최근 20판 전적 = div.GameItemList
        last_version = soup.select_one('#readme > div.Box-body.px-5.pb-5 > article > p:nth-child(5)')

        if last_version.text == version:
            return True
        else:
            return False
    else:
        print(response.status_code)


def set_detail_info():
    total_win_rate = 0
    for i in range(0, len(id_list)):
        eval(f"ex.player{i+1}Label.setText('{id_list[i]}')")
        eval(f"ex.player{i+1}Label.adjustSize()")
        if result_dict[id_list[i]]['전적'] == '없음':
            total_win_rate += 50
        else:
            most_line = result_dict[id_list[i]]['모스트 라인']
            most_champ = result_dict[id_list[i]]['모스트 챔프']
            eval(f"ex.cb_p{i+1}.setCurrentText('{most_line}')")
            eval(f"ex.champ{i+1}.setText('{most_champ}')")
            total_win_rate += int(result_dict[id_list[i]]['승률'][:-1])

            # 팀내 평균 등수 가산점 - 1: +20%, 2: +10%, 4: -10%, 5: -20%
            rank = result_dict[id_list[i]]['팀내 평균 등수']
            if rank == '1':
                total_win_rate += 20
            elif rank == '2':
                total_win_rate += 10
            elif rank == '4':
                total_win_rate -= 10
            elif rank == '5':
                total_win_rate -= 20

            # 킬 관여율 가산점 - 60 이상: +10%, 60 ~ 50: +5%, 50 ~ 40: 0%, 3: 10%, 40 ~ 30: -5%, 30% 미만: -10%
            k_r = result_dict[id_list[i]]['킬 관여율'].replace('(', '')
            kill_relate = int(k_r.replace('%)', ''))
            if kill_relate >= 60:
                total_win_rate += 10
            elif 60 > kill_relate >= 50:
                total_win_rate += 5
            elif 40 > kill_relate >= 30:
                total_win_rate -= 5
            elif 30 > kill_relate:
                total_win_rate -= 10

            # kda - 4 이상: +10%, 4 ~ 3: +5%, 2 ~ 1: -5%, 1 미만: -10%
            kda = float(result_dict[id_list[i]]['K/D/A'])
            if kda >= 4:
                total_win_rate += 10
            elif 4 > kda >= 3:
                total_win_rate += 5
            elif 2 > kda >= 1:
                total_win_rate -= 5
            elif 1 > kda:
                total_win_rate -= 10

    average_win_rate = total_win_rate / 5
    ex.winRateLabel.setText(str(round(average_win_rate)) + ' %')

    return total_win_rate


def final_calculation():
    total_win_rate = first_total_point

    for i in range(0, len(id_list)):
        if result_dict[id_list[i]]['전적'] == '없음':
            pass
        else:
            # 모스트 챔프 가산점 - +5%
            if result_dict[id_list[i]]['모스트 챔프'] == eval(f"ex.champ{i+1}.text()"):
                total_win_rate += 5

            # 모스트 라인 가산점 - +5%
            if result_dict[id_list[i]]['모스트 라인'] == eval(f"ex.cb_p{i+1}.currentText()"):
                total_win_rate += 5

    average_win_rate = total_win_rate / 5
    ex.winRateLabel2.setText(str(round(average_win_rate)) + ' %')


def get_chrome_driver_path():
    work_dir = os.getcwd()
    current_chrome_version = chromedriver_autoinstaller.get_chrome_version().split('.')[0]

    try:
        os.listdir(os.path.join(current_chrome_version))
    except FileNotFoundError:
        # chromedriver_autoinstaller.install() - download in lib path
        # use parameter anyStr - download in work_dir
        return chromedriver_autoinstaller.install('chromedriver')
    else:
        return os.path.join(work_dir, current_chrome_version, 'chromedriver.exe')


if __name__ == '__main__':
    # required for multiprocessing when run this script by exe
    multiprocessing.freeze_support()

    current_version = '1.0.0'

    # lol scouter version check
    if version_check(current_version):
        print('최신 버전입니다.')
    else:
        print('최신 버전이 아닙니다.\n업데이트 버전을 다운받으세요.\n업데이트하지 않으면 정상적으로 동작하지 않을 수 있습니다.')
        print("https://github.com/20hun/lolscouter")

    # download last version of chromedriver
    driver_path = get_chrome_driver_path()

    # op.gg url for each server
    url_list = ['https://op.gg/', 'https://jp.op.gg/', 'https://na.op.gg/', 'https://euw.op.gg/', 'https://eune.op.gg/',
                'https://eune.op.gg/', 'https://br.op.gg/', 'https://las.op.gg/', 'https://lan.op.gg/',
                'https://ru.op.gg/', 'https://tr.op.gg/']

    app = QApplication(sys.argv)

    try:
        while True:
            ex = guiWindow.MyApp()

            # until run first_event_loop.exit(), main process wait
            # for setting server, user info
            ex.first_event_loop.exec_()

            # multi process 에서 전역 변수로 사용
            manager = Manager()
            result_dict = manager.dict()

            # 선택한 multi process 만큼 pool 생성
            pool = Pool(int(ex.cb_cpu.currentText()))

            url = manager.Value(str, url_list[ex.cb.currentIndex()])
            chrome_driver_path = manager.Value(str, driver_path)
            id_list = ex.user_id_list

            pool.starmap(crawling, zip(id_list, repeat(chrome_driver_path), repeat(url), repeat(result_dict)))
            pool.close()
            pool.join()

            first_total_point = set_detail_info()

            for key_id in id_list:
                print('[' + key_id + ']')
                for key in result_dict[key_id]:
                    print(key + '\t' + result_dict[key_id][key])
                print('---------------------------')

            # for setting position, champion
            ex.second_event_loop.exec_()

            final_calculation()

            # for setting init
            ex.third_event_loop.exec_()
    except Exception:
        msg = traceback.format_exc()
        print(repr(msg))
