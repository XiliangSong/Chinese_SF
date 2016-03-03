#encoding=utf-8
#!/usr/bin/env python
import os

INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/Lucene_Index/IndexFiles_corpus_cn.index")

import sys, os, lucene, io
from collections import OrderedDict

from java.io import File
# from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

# from RPISlotFilling.utils.load_sf_query import load_sf_query


"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
# def run(searcher, analyzer):
#     while True:
#         print
#         print "Hit enter with no input to quit."
#         command = raw_input("Query:")
#         if command == '':
#             return
#
#         print
#         print "Searching for:", command
#         query = QueryParser(Version.LUCENE_CURRENT, "contents",
#                             analyzer).parse(command)
#         scoreDocs = searcher.search(query, 50).scoreDocs
#         print "%s total matching documents." % len(scoreDocs)
#
#         for scoreDoc in scoreDocs:
#             doc = searcher.doc(scoreDoc.doc)
#             print str(scoreDoc.score), ' path:', doc.get("path"), 'name:', doc.get("name")
#
#
# def main():
#     lucene.initVM(vmargs=['-Djava.awt.headless=true'])
#     print 'lucene', lucene.VERSION
#     base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
#     directory = SimpleFSDirectory(File(os.path.join(base_dir, INDEX_DIR)))
#     searcher = IndexSearcher(DirectoryReader.open(directory))
#     analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
#     run(searcher, analyzer)
#     del searcher


def search(query_name, searcher, analyzer, scale):
    query = QueryParser(Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(query_name)
    scoreDocs = searcher.search(query, scale).scoreDocs

    found_doc_path = []
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        doc_path = os.path.join('data/2014_KBP_Chinese_Source_Corpus_extracted'+
                                doc.get('path').split('2014_KBP_Chinese_Source_Corpus_extracted')[1], doc.get('name'))
        doc_text = io.open(doc_path, 'r', -1, 'utf-8').read().replace(' ', '').replace('\n', '')
        if query_name in doc_text:
            found_doc_path.append(doc_path)

    return found_doc_path[:10]


# search
def search_string(query_name, searcher, analyzer, scale):
    query = QueryParser(Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(query_name)
    scoreDocs = searcher.search(query, scale).scoreDocs

    found_doc_path = []
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        doc_path = doc.get('path')
        doc_id = doc.get('name')
        found_doc_path.append(os.path.join(doc_path, doc_id))

    del searcher

    # evaluate ir performance
    correct_doc_index = []
    for i in xrange(len(found_doc_path)):
        found_doc = io.open(found_doc_path[i].replace('/Users/boliangzhang/Desktop/', '/Users/boliangzhang/Documents/Phd/Resources/'), 'r', -1, 'utf-8').read().replace(' ', '').replace('\n', '')
        if query_name in found_doc:
            correct_doc_index.append(i)

    return correct_doc_index, found_doc_path


def init_lucene_search():
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    print 'Index ', INDEX_DIR
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # current dir
    directory = SimpleFSDirectory(File(INDEX_DIR))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = SmartChineseAnalyzer(Version.LUCENE_CURRENT, SmartChineseAnalyzer.getDefaultStopSet())

    return searcher, analyzer


def search_document(query_list):
    searcher, analyzer = init_lucene_search()
    results = OrderedDict()

    for q in query_list:
        print(q.name + '...'),
        query_name = q.name
        correct_doc_index, found_doc_path = search(query_name.replace(' ', ''), searcher, analyzer, 30000)
        if not os.path.exists('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/' +
                query_name):
            os.makedirs('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/' + query_name)

        for i in correct_doc_index:
            doc_id = found_doc_path[i].split('/')[-1]
            f = io.open(found_doc_path[i], 'r', -1, 'utf-8').read()
            f_out = io.open('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/' +
                            query_name + '/' + doc_id, 'w', -1, 'utf-8')
            f_out.write(f)
            f_out.close()

            try:
                results[query_name].append(doc_id)
            except KeyError:
                results[query_name] = [doc_id]
        print('Done')

    return results


def search_evaluation_doc():
    # evaluation
    queries = load_sf_query('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/'
                            'tac_kbp_2014_chinese_regular_slot_filling_evaluation_queries.xml')

    # lucene search source documents
    lucene_query_doc_id = search_document(queries)

    ldc_source_corpus_dir = \
        '../../data/LDC/LDC2014E123_TAC_KBP_2014_Chinese_Regular_Slot_Filling_Training_Data/data/source_doc/'

    ldc_hits = 0
    lucene_hits = 0
    overlap_hits = 0
    for q in queries:
        if not lucene_query_doc_id[q]:
            continue
        ldc_doc_id = retrieve_query_document(q, ldc_source_corpus_dir).keys()
        ldc_doc_id = [doc_id.lower() for doc_id in ldc_doc_id]
        ldc_hits += len(ldc_doc_id)

        lucene_doc_id = lucene_query_doc_id[q.name]
        lucene_hits += len(lucene_doc_id)

        overlap = set(ldc_doc_id).intersection(set(lucene_doc_id))
        overlap_hits += len(overlap)

        print(q.name + ' ' + 'ldc_doc_id:' + str(len(ldc_doc_id)) + ' eval_doc_id:' + str(len(lucene_doc_id)) +
              ' overlap:' + str(len(overlap)))

    print('ldc hits: ' + str(ldc_hits))
    print('lucene hits: ' + str(lucene_hits))
    print('overlap hits: ' + str(overlap_hits))

    return


def search_insufficient_doc_query():
    dir = '../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/'
    fnms = os.listdir(dir)

    count = 0
    unique_docs = set()
    for fnm in fnms:
        if fnm == '.DS_Store':
            continue
        docs = os.listdir(dir + fnm)
        docs = [d.strip() for d in docs]
        unique_docs = unique_docs.union(set(docs))
        count += len(docs)
        # if len(docs) < 5:
        print(fnm + ' ' + str(len(docs)))
    print('totally ' + str(count) + ' query docs')
    print('totally ' + str(len(unique_docs)))
    return


def main():
    searcher, analyzer = init_lucene_search()

    test_set = [u'韦尔奇', u'郭全宝', u'卓琳', u'高秀敏', u'洪一峰', u'武衡', u'陈妙华', u'徐子淇', u'秦厚修', u'王梓木',
                u'敬一丹', u'肖毅', u'李修平', u'朱剑凡', u'林传凯', u'王宁', u'麦嘉轩', u'茅以升', u'毛泽东', u'邓小平', u'周恩来']

    results = OrderedDict()
    for query in test_set:
        correct_doc_index, found_doc_path = search(query, searcher, analyzer)

        results[query] = found_doc_path

        if not correct_doc_index:
            precision = 0
            last_correct_doc_index = 0
        else:
            last_correct_doc_index = correct_doc_index[-1] + 1
            precision = float(len(correct_doc_index)) / last_correct_doc_index

        print(query + ' ' + str(len(correct_doc_index)) + '/' +
              str(last_correct_doc_index) + '=' + str(precision))
        print(correct_doc_index)
        print('total returns ' + str(len(found_doc_path)) + '\n')

    return


# retrieve documents that contain query
def retrieve_query_document(query, corpus_dir):
    query_name = query.name

    fnms = os.listdir(corpus_dir)

    relevant_doc = OrderedDict()

    for fnm in fnms:
        if fnm == '.DS_Store':
            continue
        # if fnm == 'XIN_CMN_20040529.0015':
        #     pass
        f = io.open(os.path.join(corpus_dir, fnm), 'r', -1, 'utf-8').read()
        if query_name in f:
            relevant_doc[fnm] = f

    return relevant_doc

if __name__ == '__main__':
    # main()
    # search_evaluation_doc()
    search_insufficient_doc_query()