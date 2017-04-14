# -*- coding: utf-8 -*-
# filename: common.py


def date_to_weekday(dt):
    m_dic = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    return m_dic[dt.weekday()]
