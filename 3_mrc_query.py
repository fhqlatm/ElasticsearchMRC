from elasticsearch import Elasticsearch
from colorama import init, Fore, Back, Style
init(autoreset=True)
import argparse
from pororo import Pororo

def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-query", default='2차 세계대전은 언제 종전되었는가?', type=str)
    parser.add_argument("-searchsize", default=5, type=int)

    return parser

def main():
    args = getParser().parse_args()
    init(autoreset=True)

    es = Elasticsearch("http://127.0.0.1:9200/")
    es.info()

    mrc = Pororo(task="mrc", lang="ko")
    query = args.query
    print(f'{Back.RED + Fore.WHITE}Query: {query}')

    index_name = 'texts'
    results = es.search(index=index_name, body={'from':0, 'size':args.searchsize, 'query':{'match':{'text': query}}})

    for i, result in enumerate(results['hits']['hits']):
        id = result['_source']['id']
        score = result['_score']
        text = result['_source']['text']

        mrc_result = mrc(query, text, postprocess=True)

        answer = mrc_result[0]
        start = text.find(answer)
        end = start + len(answer)
        
        print(f'{Back.GREEN + Fore.WHITE}Similarity Rank {i+1} | Document id ({id}) | Score: {score}')
        print(f'Text: \n{text[:start] + Back.BLUE + Fore.WHITE} {answer} {Style.RESET_ALL + text[end:]}')
        print('-----------------------------------------------------------')


if __name__ == "__main__":
    main()