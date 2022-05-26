from tqdm import tqdm
from Korpora import Korpora
from elasticsearch import Elasticsearch

def getDocuments():
    # kowikitext 데이터는 총 88만여 개의 Articles로 구성
    # text 길이를 고려하여 약 300만여 개의 데이터로 dataset 구성
    # train data는 약 99%, dev data 및 test data는 각각 0.5%
    kowikitext = Korpora.load('kowikitext')

    id = 0
    dataset = []
    for text in tqdm(kowikitext.train.texts):
        if len(text) > 15:
            dataset.append({'id': id, 'text': text})
            id += 1
    for text in tqdm(kowikitext.dev.texts):
        if len(text) > 15:
            dataset.append({'id': id, 'text': text})
            id += 1
    for text in tqdm(kowikitext.test.texts):
        if len(text) > 15:
            dataset.append({'id': id, 'text': text})
            id += 1
    
    return dataset

def make_index(es, index_name):
    # create index
    # 이미 index가 존재하면 삭제 후 새롭게 생성
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name)

def main():
    # 구동되고 있는 Elasticsearch 엔진과 연결
    es = Elasticsearch("http://127.0.0.1:9200/")
    es.info()

    # Korpora의 한국어 위키피디아 데이터셋을 불러와 저장 후 index 생성
    dataset = getDocuments()

    index_name = 'texts'
    make_index(es, index_name)

    # Elasticsearch 엔진에 index 저장
    for i, doc in enumerate(tqdm(dataset, ascii=True, ncols=150)):
        es.index(index=index_name, doc_type='string', body=doc)

        if i % 10000 == 0:
            es.indices.refresh(index=index_name)

    es.indices.refresh(index=index_name)

if __name__ == "__main__":
  main()
