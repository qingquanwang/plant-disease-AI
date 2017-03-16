# plant-disease-AI
expert system of plants disease diagnostics


Tools:
1. build-content-index.py: generate inverse list of contents, Index:[type + keyword] -> list(content, relevance), Index-sensitivity

2. build-dict.py: build name -> entityId(type + ID)  entityId -> list(entity_attribute:[attribute_key:string, list(attribute_value:string)])
   usage: ./build-dict.py --data_root=./data/dict --output=./data/build/name.dic; cat data/build/name.dic | sort -t$'\t' -k2 > ./data/build/name.dic.sorted


3. nlu-simulator.py: 
    input: state:(taskId + list(parameter: [parameter-name, list(parameter-value:string)])), question(text)
    output: state, text understanding sequence( [w1 w2][entityId] [w3][entityId] w4 w5 )

4. nlr-simulator.py:
    input: state
    output: question(text), reply indicator: expected state(asking value is indicated by ?)

5. dialog-simulator.py: command line dialog simulator

6. server tools:
    1) start, restart, stop server
    2) uninstall, reinstall, install the environment


code structure:
1. backend:
    1.1 ContentManager.py: class of content manager, cleaning content data & extracting keyword & building index
        - ContentIndex.py: class of Index, Index <- [Type, Keyword, Sensitivity]
        
    1.2 DictManager.py: class of dict manager, building dict and supporting ngram and other lookup methods
    1.3 State.py: class of representation of state
    1.4 nlu.py: class of nlu methods, tagging keyword, generating candidate sequences, scoring the best seq, output the understanding
    1.5 nlr.py: class of nlr methods, generating reply from the current state
    1.6 Collector.py: class of logging,collecting the dialog data, maintaining the history
    1.7 DialogManager.py: class of controling the dialog flow, maintaining the whiteboard parameters and state transitioning


data structure:
1. State: state-def.txt
    a graph of tasks, starting from node "Welcome"
    For each task T:
        nlr(T, Env) is the reply message for task T
        |
        |
        V
        nlu(text, T, Env) is the understanding of text within context
        |
        |
        V
        transition(TaskHistory, T, &Env) returns the nextTask and Env

2. dict:
    name-dict.dat: key:string \t value: list(entityId)
    entity-dict.dat: key: entityId \t value: list(entity_attribute:[attribute_key:string, list(attribute_value:string)])

3. content:
    content-index.dat: Index -> list(ContentId, relevance)
    content-pool.dat: ContentId -> Content

