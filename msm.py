#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire
from plantDiseaseAI.backend.preprocessor.zhBookPreprocess import *


def tst_zhBookPreprocess(rawText):
    toks = []
    processor = ZhBookPreprocessor()
    processor.preprocess(rawText, toks)
    for tok in toks:
        print(tok)


if __name__ == '__main__':
    fire.Fire()
