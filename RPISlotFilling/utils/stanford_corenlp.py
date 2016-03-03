__author__ = 'boliangzhang'

import os
import shutil
import io

from RPISlotFilling.lib.corenlp.corenlp import batch_parse


def stanford_parser(sentences, proc_id=0):
    # print('Im stanford parsing process'+proc_id)
    if os.path.exists('data/.tmp'+proc_id):
        shutil.rmtree('data/.tmp'+proc_id)
    os.makedirs('data/.tmp'+proc_id)  # create a temperal dir for parsing large paragraphs

    for sent_id in sentences.keys():
        f = io.open(os.path.join('data/.tmp'+proc_id, sent_id), 'w', -1, 'utf-8')
        f.write(sentences[sent_id])
        f.close()
    stanford_parser_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '../../externals/stanford-corenlp-full-2014-08-27/')
    parsing_result = list(batch_parse('data/.tmp'+proc_id,
                                      stanford_parser_dir,
                                      properties=os.path.join(stanford_parser_dir, "StanfordCoreNLP-chinese.properties")
                                      ))
    result = dict()
    for r in parsing_result:
        result[r['file_name']] = r['sentences'][0]

    return result
