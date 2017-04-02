#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import fire
from plantDiseaseAI.backend.preprocessor.zhBookPreprocess import *


def tst_zhBookPreprocess(rawText):
    processor = ZhBookPreprocessor()
    if os.path.isfile(rawText):
        with open(rawText, mode='r') as f:
            for line in f:
                toks = []
                line = line.strip()
                processor.preprocess(line, toks)
                print(','.join(str(tok) for tok in toks))
    else:
        toks = []
        processor.preprocess(rawText, toks)
        print(','.join(str(tok) for tok in toks))


if __name__ == '__main__':
    fire.Fire()
