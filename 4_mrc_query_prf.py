from audioop import reverse
from elasticsearch import Elasticsearch
from colorama import init, Fore, Back, Style
init(autoreset=True)
import argparse
from pororo import Pororo

def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-query", default='제2차 세계대전은 언제 종전되었는가?', type=str)
    parser.add_argument("-searchsize", default=5, type=int)
    parser.add_argument("-expansionsize", default=5, type=int)

    return parser

def main():
    args = getParser().parse_args()
    init(autoreset=True)

    es = Elasticsearch("http://127.0.0.1:9200/")
    es.info()

    mrc = Pororo(task="mrc", lang="ko")
    summ = Pororo(task="summary", lang="ko")

    query = args.query
    print(f'{Back.RED + Fore.WHITE}Query: {query}')

    index_name = 'texts'
    results = es.search(index=index_name, body={'from':0, 'size':args.searchsize, 'query':{'match':{'text': query}}})

    extended_queries = []
    extended_results = []
    search_ids = []
    rank = 0
    
    for i, result in enumerate(results['hits']['hits']):
        id = result['_source']['id']
        score = result['_score']
        text = result['_source']['text']

        summ_result = summ(text)
        mrc_result = mrc(query, text, postprocess=True)

        extended_queries.append(summ_result)
    
    for extended_query in extended_queries:
        extended_search_results = es.search(index=index_name, body={'from':0, 'size':args.expansionsize, 'query':{'match':{'text': extended_query}}})

        for i, extended_search_result in enumerate(extended_search_results['hits']['hits']):
            id = extended_search_result['_source']['id']
            score = extended_search_result['_score']
            text = extended_search_result['_source']['text']

            if id not in search_ids:
                search_ids.append(id)
                extended_results.append({'id':id, 'score':score, 'text':text})

    for extended_result in sorted(extended_results, key=lambda x: x['score'], reverse=True):
            id = extended_result['id']
            score = extended_result['score']
            text = extended_result['text']

            mrc_result_extended = mrc(query, text, postprocess=True)

            answer = mrc_result_extended[0]
            start = text.find(answer)
            end = start + len(answer)
            
            if answer != "":
                rank += 1
                print(f'{Back.GREEN + Fore.WHITE}Similarity Rank {rank} | Document id ({id}) | Score: {score}')
                print(f'Text: \n{text[:start] + Back.BLUE + Fore.WHITE} {answer} {Style.RESET_ALL + text[end:]}')
                print('-----------------------------------------------------------')

if __name__ == "__main__":
    main()