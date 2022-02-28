import os
import sys
import time

import re
from PyQt5.QtWidgets import QApplication
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager
from itertools import repeat
import multiprocessing
import traceback

from common import guiWindow

__author__ = 'Yeonghun Lee <lyhgod@gmail.com>'


def my_analysis(my_id, my_url):
    headers = {'Accept-Language': 'ko'}
    html = requests.get('https://your.gg/'+my_url+'/profile/'+my_id+'?mc=SoloRank', headers=headers).text
    soup = BeautifulSoup(html, 'lxml')

    total_div = soup.select_one('div.col-lg-8.col-12 > div.d-flex.flex-column.mt-3')
    game_list = total_div.select('div.card.gg-matchlist.py-3.px-1.px-lg-3')

    game_arrange_info_list = []

    # 이겼을 때 팀원의 평균 능력치 산출
    for game in game_list:
        member_info_list = []
        if game.find('div', 'text-w mt-1') is None:
            pass
        else:
            # 승리한 경우만
            team_member_list = game.select('div.d-flex.flex-column.justify-content-between.text-truncate > span.text-small')
            for team_member in team_member_list[:5]:
                info_id_pos_champ = team_member.select_one('img')['alt']
                separate_space_info_list = info_id_pos_champ.split(' ')
                position_list = ['탑', '정글', '미드', '원딜', '서폿']
                index_check = 0
                position = ''
                for info in reversed(separate_space_info_list):
                    if info in position_list:
                        position = info
                        break
                    else:
                        index_check += 1

                index_pos = len(separate_space_info_list) - 1 - index_check
                info_id = ''.join(separate_space_info_list[:index_pos])
                member_info_list.append([info_id, position, info_id_pos_champ.split(position + ' ')[-1]])

            game_arrange_info_list.append(member_info_list)
            # game_arrange_info_list = [[['id1', '탑', '이렐리아'], ['id2', '정글', '비에고'], ..], [['id1', 'position' ...]]

    total_average_ability = 0
    for game_set in game_arrange_info_list:
        average_ability = 0
        average_cnt = 5
        for game in game_set:
            headers = {'Accept-Language': 'ko'}
            html = requests.get('https://your.gg/' + my_url + '/profile/' + game[0] + '?mc=SoloRank',
                                headers=headers).text
            soup = BeautifulSoup(html, 'lxml')

            most_champ_list = soup.select('div.d-flex.flex-column.justify-content-center.h-100 > div')

            if not most_champ_list:
                print(game[0])
                print('검색할 수 없는 id')
                average_cnt -= 1
            else:
                # 몇 인분 했는지 확인
                my_ability = float(soup.select('div.d-flex.justify-content-center.align-items-center.gg-important-number > a')[1].text.replace(' ', '').replace('\n', ''))
                for champ in most_champ_list:
                    champ_info_txt = champ.select_one('span > img')['alt']
                    champ_info_list = re.split(r'모스트[0-9] ', champ_info_txt)
                    if champ_info_list[-1] == game[2]:
                        # 몇 인분 교체
                        my_ability = float(champ.select_one('span.ml-2.text-center > span').text.replace(' ', '').replace('\n', ''))
                        break

                # id1 모스트 라인 원딜
                most_line = soup.select_one('div.col-3.d-flex.flex-column.justify-content-end > div > div > img')['alt']
                if most_line.split(' ')[-1] != game[1]:
                    # 주력 라인이 아닌데 승리 -> if 주력 라인 -> 더 잘했을 것 -> +0.01
                    # detail_check 에서 주력 라인 아니면 -0.01
                    my_ability += 0.01
                average_ability += my_ability
        total_average_ability += average_ability/average_cnt

    average_win_ability = round(total_average_ability/len(game_arrange_info_list), 2)
    print(average_win_ability)
    return average_win_ability


def crawling(pool_id, pool_url, pool_dict):
    output_dict = {}

    headers = {'Accept-Language': 'ko'}
    html = requests.get('https://your.gg/' + pool_url.value + '/profile/' + pool_id + '?mc=SoloRank', headers=headers).text
    soup = BeautifulSoup(html, 'lxml')

    try:
        my_ability = float(
            soup.select('div.d-flex.justify-content-center.align-items-center.gg-important-number > a')[1].text.replace(
                ' ', '').replace('\n', ''))
        output_dict['평균 능력'] = my_ability

        most_champ_list = soup.select('div.d-flex.flex-column.justify-content-center.h-100 > div')
        champ_dict = {}
        for champ in most_champ_list:
            champ_info_txt = champ.select_one('span > img')['alt']
            champ_info_list = re.split(r'모스트[0-9] ', champ_info_txt)
            champ_name = champ_info_list[-1]
            champ_dict[champ_name] = float(
                    champ.select_one('span.ml-2.text-center > span').text.replace(' ', '').replace('\n', ''))

        output_dict['모스트 챔프'] = champ_dict

        # id1 모스트 라인 원딜
        most_line = soup.select_one('div.col-3.d-flex.flex-column.justify-content-end > div > div > img')['alt']
        output_dict['모스트 라인'] = most_line.split(' ')[-1]
    except IndexError:
        output_dict['평균 능력'] = '검색 불가'

    pool_dict[pool_id] = output_dict


def version_check(version):
    response = requests.get('https://github.com/20hun/lolscouter')

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    last_version = soup.select_one('#readme > div.Box-body.px-5.pb-5 > article > p:nth-child(5)')

    if last_version.text == version:
        return True
    else:
        return False


def set_detail_info():
    for i in range(0, len(id_list)):
        eval(f"ex.player{i+1}Label.setText('{id_list[i]}')")
        eval(f"ex.player{i+1}Label.adjustSize()")
        if result_dict[id_list[i]]['평균 능력'] == '검색 불가':
            eval(f"ex.cb_champ{i+1}.addItem('정보 없음')")
        else:
            most_line = result_dict[id_list[i]]['모스트 라인']
            most_champ_dict = result_dict[id_list[i]]['모스트 챔프']
            most_champ_list = list(most_champ_dict.keys())
            most_champ_list.append('그 외 다른 챔피언')
            eval(f"ex.cb_p{i+1}.setCurrentText('{most_line}')")
            eval(f"ex.cb_champ{i+1}.addItems({most_champ_list})")


def final_calculation():
    detail_sum_ability = 0
    for i in range(0, len(id_list)):
        if result_dict[id_list[i]]['평균 능력'] == '검색 불가':
            pass
        else:
            if eval(f"ex.cb_champ{i+1}.currentText()") == '그 외 다른 챔피언':
                detail_sum_ability += result_dict[id_list[i]]['평균 능력']
            else:
                detail_sum_ability += result_dict[id_list[i]]['모스트 챔프'][eval(f"ex.cb_champ{i+1}.currentText()")]

            if result_dict[id_list[i]]['모스트 라인'] != eval(f"ex.cb_p{i+1}.currentText()"):
                detail_sum_ability -= 0.01

    average_detail_ability = detail_sum_ability / search_team_member_cnt
    detail_win_rate_impact = int(round((average_detail_ability - team_result_ability) * 100, 0))

    ex.winRateLabel2.setText(str(50 + detail_win_rate_impact) + ' %')


if __name__ == '__main__':
    # required for multiprocessing when run this script by exe
    multiprocessing.freeze_support()

    current_version = '1.1.0'

    # lol scouter version check
    # certificate_verify_failed error in mac - https://www.codeit.kr/community/threads/19775
    if version_check(current_version):
        print('최신 버전입니다.')
    else:
        print('최신 버전이 아닙니다.\n업데이트 버전을 다운받으세요.\n업데이트하지 않으면 정상적으로 동작하지 않을 수 있습니다.')
        print("https://github.com/20hun/lolscouter")

    # op.gg url for each server
    url_list = ['kr', 'jp', 'na', 'euw', 'eune', 'oce', 'br', 'las', 'lan', 'ru', 'tr']

    app = QApplication(sys.argv)

    try:
        while True:
            ex = guiWindow.MyApp()

            # until run first_event_loop.exit(), main process wait
            # for setting server, user info
            ex.first_event_loop.exec_()

            team_result_ability = my_analysis(ex.cb_id.currentText(), url_list[ex.cb.currentIndex()])

            # multi process 에서 전역 변수로 사용
            manager = Manager()
            result_dict = manager.dict()

            # 선택한 multi process 만큼 pool 생성
            pool = Pool(int(ex.cb_cpu.currentText()))

            url = manager.Value(str, url_list[ex.cb.currentIndex()])
            id_list = ex.user_id_list

            pool.starmap(crawling, zip(id_list, repeat(url), repeat(result_dict)))
            pool.close()
            pool.join()

            current_team_total_ability = 0
            search_team_member_cnt = 5

            for key_id in id_list:
                # {'평균 능력': 1.01, '모스트 챔프': {'빅토르': 1.24, '베이가': 0.83, '야스오': 0.88}, '모스트 라인': '미드'}
                # {'평균 능력': '검색 불가'}
                print('[' + key_id + ']')
                if result_dict[key_id]['평균 능력'] == '검색 불가':
                    search_team_member_cnt -= 1
                else:
                    current_team_total_ability += result_dict[key_id]['평균 능력']
                print(result_dict[key_id])
                print('---------------------------')

            average_current_team_ability = round(current_team_total_ability/search_team_member_cnt, 2)

            win_rate_impact = int(round((average_current_team_ability - team_result_ability) * 100, 0))

            ex.winRateLabel.setText(str(50 + win_rate_impact) + ' %')

            set_detail_info()

            # for setting position, champion
            ex.second_event_loop.exec_()

            final_calculation()

            # for setting init
            ex.third_event_loop.exec_()
    except Exception:
        msg = traceback.format_exc()
        print(repr(msg))
