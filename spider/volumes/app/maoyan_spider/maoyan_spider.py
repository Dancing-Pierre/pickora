# -*- coding: utf-8 -*-
"""
猫眼电影「正在热映」采集脚本

- 每天凌晨 2 点触发一次（脚本内 while + 时间窗口判断，沿用 tjd_statist_script 模式）
- 翻页采集 offset=0,18,36... 直到某页不足 18 条为止
- 仅采集列表页字段，xpath 解析
- 采集成功：今天 movieid 集合外的在映记录置 state=0(过期)，集合内的 upsert 并置 state=1
- 采集失败（首页取不到数据）：保留库内现有状态不动
"""
import os
import sys
import time
import datetime

import requests
from lxml import etree
import pymysql

sys.path.append('../')
from common import config
from common import common

# 每页影片数，与 config.ini 的 page_size 保持一致
PAGE_SIZE = int(config.spider_config.get('page_size', '18'))

# 列表页单部影片的卡片 xpath（class 同时包含 movie-item 与 film-channel）
CARD_XPATH = '//div[contains(@class, "movie-item") and contains(@class, "film-channel")]'

# 全局评分节点 xpath（与卡片在文档中一一对应，按索引配对）
SCORE_XPATH = '//div[contains(@class, "channel-detail-orange")]'

# upsert：以 movieid 唯一键为准，命中则更新业务字段并重置在映状态
UPSERT_SQL = """
INSERT INTO maoyan_film (
    movieid, name, detail_url, poster, type, actors, release_date,
    score, version_tags, ticket_buy, state, crawl_date
) VALUES (
    %(movieid)s, %(name)s, %(detail_url)s, %(poster)s, %(type)s, %(actors)s,
    %(release_date)s, %(score)s, %(version_tags)s, %(ticket_buy)s, 1, %(crawl_date)s
)
ON DUPLICATE KEY UPDATE
    name        = VALUES(name),
    detail_url  = VALUES(detail_url),
    poster      = VALUES(poster),
    type        = VALUES(type),
    actors      = VALUES(actors),
    release_date= VALUES(release_date),
    score       = VALUES(score),
    version_tags= VALUES(version_tags),
    ticket_buy  = VALUES(ticket_buy),
    state       = 1,
    crawl_date  = VALUES(crawl_date)
"""

# 把今天没采到的、当前仍在映(state=1)的记录置为过期(state=0)
# 不预格式化占位符：在 to_job 里按 movieid 数量动态生成 IN(%s,...) 后交 pymysql 参数化执行


class Work(object):
    RUN_NAME = '猫眼正在热映定时采集'

    def __init__(self):
        self._init_param()
        self._init_mysql()
        self._init_session()

    def _init_param(self):
        # runtime 形如 [['0200', '0205']]
        self.runtime = [a.split(',') for a in config.work_time.get('maoyan_spider', '').split('|') if a]
        self.interval = config.heartbeat
        self.base_url = config.spider_config.get('base_url')
        self.max_pages = int(config.spider_config.get('max_pages', '30'))
        self.request_interval = float(config.spider_config.get('request_interval', '1'))
        self.request_timeout = int(config.spider_config.get('request_timeout', '15'))
        self.max_retries = int(config.spider_config.get('max_retries', '3'))
        self.last_run_file = '/logs/maoyan_last_run_date.txt'

    def _init_mysql(self):
        self.mc = common.get_mysql_conn()

    def _init_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.maoyan.com/',
        })

    # -------------------- 调度辅助 --------------------

    def _get_last_run_date(self):
        try:
            with open(self.last_run_file, 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, IOError):
            return ''

    def _save_last_run_date(self, run_date):
        try:
            os.makedirs(os.path.dirname(self.last_run_file), exist_ok=True)
            with open(self.last_run_file, 'w') as f:
                f.write(run_date)
        except IOError as e:
            print("{} 无法保存 last_run_date: {}".format(datetime.datetime.now().__str__(), e))

    # -------------------- 采集 --------------------

    def _fetch_page(self, offset):
        url = '{}{}'.format(self.base_url, offset)
        for attempt in range(1, self.max_retries + 1):
            try:
                r = self.session.get(url, timeout=self.request_timeout)
                if r.status_code == 200 and 'movie-item film-channel' in r.text:
                    return r.text
                print("{} 请求 offset={} 第{}次异常 status={} len={}".format(
                    datetime.datetime.now().__str__(), offset, attempt, r.status_code, len(r.text)))
            except BaseException as e:
                print("{} 请求 offset={} 第{}次异常: {}".format(
                    datetime.datetime.now().__str__(), offset, attempt, e))
            time.sleep(self.request_interval * attempt)
        return None

    @staticmethod
    def _parse_card(card, score_text):
        """解析单部影片卡片，返回字段 dict；解析失败返回 None"""
        href_list = card.xpath('.//a[contains(@href, "/films/")]/@href')
        if not href_list:
            return None
        href = href_list[0]
        movieid = ''.join(ch for ch in href if ch.isdigit())
        if not movieid:
            return None

        name_list = card.xpath('.//span[contains(@class, "name")]/text()')
        name = name_list[0].strip() if name_list else ''

        poster_list = card.xpath('.//div[@class="movie-poster"]//img/@data-src')
        poster = poster_list[0].strip() if poster_list else ''

        # 类型 / 主演 / 上映时间，靠 hover-tag 文本区分
        type_, actors, release_date = '', '', ''
        for title_div in card.xpath('.//div[contains(@class, "movie-hover-title")]'):
            label_list = title_div.xpath('./span[@class="hover-tag"]/text()')
            if not label_list:
                continue
            label = label_list[0]
            value = title_div.xpath('string(.)').strip()
            if value.startswith(label):
                value = value[len(label):].strip()
            if '类型' in label:
                type_ = value
            elif '主演' in label:
                actors = value
            elif '上映' in label:
                release_date = value

        # 版本标识 imax2d / 3d 等
        ver_tags = card.xpath('.//div[@class="movie-ver"]//i/@class')
        version_tags = ','.join(t.strip() for t in ver_tags if t.strip())

        # 是否售票中
        ticket_buy = 1 if card.xpath('.//div[contains(@class, "channel-action-sale")]') else 0

        # 评分：列表页多为"暂无评分"，记为空；有数值则原样保留
        score = ''
        if score_text and '暂无评分' not in score_text:
            score = score_text.strip()

        return dict(
            movieid=movieid,
            name=name,
            detail_url='https://www.maoyan.com' + href,
            poster=poster,
            type=type_,
            actors=actors,
            release_date=release_date,
            score=score,
            version_tags=version_tags,
            ticket_buy=ticket_buy,
        )

    def crawl(self):
        """翻页采集，返回 {movieid: film_dict}；首页就失败返回 None"""
        films = {}
        for page in range(self.max_pages):
            offset = page * PAGE_SIZE
            html = self._fetch_page(offset)
            if html is None:
                print("{} offset={} 取数失败".format(datetime.datetime.now().__str__(), offset))
                if page == 0:
                    return None
                break

            tree = etree.HTML(html)
            cards = tree.xpath(CARD_XPATH)
            score_nodes = tree.xpath(SCORE_XPATH)
            if not cards:
                print("{} offset={} 无影片卡片，结束翻页".format(datetime.datetime.now().__str__(), offset))
                break

            for idx, card in enumerate(cards):
                score_text = score_nodes[idx].xpath('string(.)') if idx < len(score_nodes) else ''
                film = self._parse_card(card, score_text)
                if film:
                    films[film['movieid']] = film

            print("{} offset={} 解析 {} 部，累计 {} 部".format(
                datetime.datetime.now().__str__(), offset, len(cards), len(films)))

            if len(cards) < PAGE_SIZE:
                break
            time.sleep(self.request_interval)

        return films if films else None

    # -------------------- 入库 --------------------

    def to_job(self, now_date):
        print(datetime.datetime.now().__str__(), 'INFO',
              __file__ + ':' + str(sys._getframe().f_lineno), '开始执行采集任务', now_date)
        try:
            films = self.crawl()
            if not films:
                print("{} 采集失败或无数据，保留库内现有状态".format(datetime.datetime.now().__str__()))
                return

            today = datetime.date.today().isoformat()
            movieids = list(films.keys())
            rows = [dict(f, crawl_date=today) for f in films.values()]

            # 直接用 pymysql cursor 执行，绕开 exec_cmd：
            # exec_cmd 对 list 参数会走 executemany（按行批量），而 EXPIRE 的 IN(...)
            # 是单条 SQL 配 N 个标量参数，传 list 会被误判为批量，导致占位符数量不匹配。
            self.mc.check_connect()
            cursor = self.mc.get_cursor

            # 1. 今天没采到的在映记录置过期：movieid 转 tuple 作为单条 SQL 的位置参数
            placeholders = ','.join(['%s'] * len(movieids))
            expire_sql = "UPDATE maoyan_film SET state = 0 WHERE state = 1 AND movieid NOT IN ({})".format(placeholders)
            cursor.execute(expire_sql, tuple(movieids))
            print("{} 置过期完成，今天共采到 {} 部".format(
                datetime.datetime.now().__str__(), len(movieids)))

            # 2. 今天采到的 upsert 并置在映：批量执行，统一提交
            cursor.executemany(UPSERT_SQL, rows)
            self.mc.get_conn.commit()
            print("{} 入库完成，upsert {} 条".format(
                datetime.datetime.now().__str__(), len(rows)))

        except pymysql.Error as e:
            print("{} pymysql.Error: {}".format(datetime.datetime.now().__str__(), e))
            self._init_mysql()
        except BaseException as e:
            print("{} 采集入库异常: {}".format(datetime.datetime.now().__str__(), e))


if __name__ == '__main__':
    print('=' * 10, Work.RUN_NAME, '=' * 10, datetime.datetime.now().__str__(), '=' * 20)
    worker = Work()
    print(datetime.datetime.now().__str__(), 'INFO', 'runtime=', worker.runtime, 'interval=', worker.interval)

    # flush：手动执行一次，不等待时间窗口
    if len(sys.argv) >= 2 and sys.argv[1] == 'flush':
        now = datetime.datetime.now()
        worker.to_job(now.strftime('%Y%m%d'))
        print(datetime.datetime.now().__str__(), 'INFO', '手动执行完成')
    else:
        while True:
            now = datetime.datetime.now()
            now_date = now.strftime('%Y%m%d')
            now_time = now.strftime('%H%M')

            for runtime in worker.runtime:
                if int(runtime[0]) <= int(now_time) <= int(runtime[1]):
                    # 每天只执行一次：当日已跑过则跳过
                    if worker._get_last_run_date() != now_date:
                        worker.to_job(now_date)
                        worker._save_last_run_date(now_date)
                    time.sleep(worker.interval)
                    break
            else:
                time.sleep(60 * 10)
