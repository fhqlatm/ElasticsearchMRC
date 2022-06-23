from elasticsearch import Elasticsearch
from colorama import init, Fore, Back, Style
import argparse

def getParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-query", default='2차 세계대전', type=str)
    parser.add_argument("-searchsize", default=5, type=int)

    return parser

def main():
    args = getParser().parse_args()
    init(autoreset=True)

    es = Elasticsearch("http://127.0.0.1:9200/")
    es.info()

    query = args.query
    print(f'{Back.RED + Fore.WHITE}Query: {query}')

    index_name = 'texts'
    results = es.search(index=index_name, body={'from':0, 'size':args.searchsize, 'query':{'match':{'text': query}}})

    for i, result in enumerate(results['hits']['hits']):
        id = result['_source']['id']
        score = result['_score']
        text = result['_source']['text']

        print(f'{Back.GREEN + Fore.WHITE}Similarity Rank {i+1} | Document id ({id}) | Score: {score}')
        print(f'Text: \n{text}')
        print('-----------------------------------------------------------')

if __name__ == "__main__":
  main()
