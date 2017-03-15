# -*- coding: utf-8 -*-
import os


def lstr(msg):
    file_path = os.path.join('../../../../webpy_logs/', 'log.txt')
    with open(file_path, 'a') as log_file:
        log_file.write(msg + '\n')


def luni(msg):
    lstr(msg.encode('utf-8'))
