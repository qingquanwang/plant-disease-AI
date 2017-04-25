# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.handler.basicHandler import *
from plantDiseaseAI.utils.binhai.bh_manager import *
from tools.gov.govTitleExtracter import *


class DisplayBHHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(DisplayBHHandler, self).__init__(params, modules)
        self._msgTemplateId = params['msg']['tipsTemplateId']
        # set gov module
        gov_name = 'GOV'
        self._indexer = modules[gov_name]

    def accepted(self, state):
        return self.has_domain(state)

    def execute(self, state, userInput, actions):
        # env = state._session._env
        if state._status == 'Run':
            action = Action('ShowPlainText')
            action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
            actions.append(action)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            state._status = 'WaitTextInput'

            anaList = []
            blocks = {}
            self._nlu.tagText(anaList, userInput._input, True)
            self._semantic.extract(anaList, blocks, '')
            blockStr = json.dumps(blocks, encoding='utf-8')

            idxs = []
            attrs = []
            self._indexer.extractFeature(blocks, idxs, attrs)
            #pp.pprint(idxs)
            cands = []
            self._indexer.getCandidate(cands, idxs, attrs)
            print userInput._input.encode('utf-8')
            for cand in cands:
                doc = self._indexer._content[cand]
                print '  ' + cand.encode('utf-8') + '\t' + doc['title'].encode('utf-8')
            exit()
            # result = []
            # mgr = BHManager()
            # urls = [
            #     'live/20151221/75414.shtm',
            #     # 'http://tj.bendibao.com/live/2017317/79538.shtm'
            # ]
            # img_set = False
            # if len(urls) > 1:
            #     # 有多条结果时，显示背景图
            #     item0 = {}
            #     item0['title'] = '查询“' + userInput._input + '” powered by Cogik'
            #     item0['desc'] = ''
            #     item0['picurl'] = 'http://www.xiaogu-tech.com/img/wx/cogik-rect.png'
            #     img_set = True
            #     item0['url'] = 'http://www.xiaogu-tech.com/'
            #     result.append(item0)
            # for url in urls:
            #     ab_url, title, desc = mgr.fetch_live_content(url)
            #     item = {}
            #     item['title'] = title.encode('utf-8')
            #     item['desc'] = desc.encode('utf-8')
            #     if not img_set:
            #         item['picurl'] = 'http://www.xiaogu-tech.com/img/wx/cogik-rect.png'
            #     else:
            #         item['picurl'] = ''
            #     item['url'] = ab_url
            #     result.append(item)
            # json_str = json.dumps(result, ensure_ascii=False)


            action = Action('ShowNewsText')
            action.setText(json_str.decode('utf-8'))
            actions.append(action)
            return True
        else:
            return True
