# coding=utf-8
__author__ = 'boliangzhang'

import io
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader


def visualizer(queries, sf_answers, path):
    env = Environment(loader=FileSystemLoader(['RPISlotFilling/visualization/']),
                      extensions=['jinja2.ext.do'])
    env.filters['count_l'] = count_l

    template = env.get_template('mainpage.html')

    html = template.render(queries=queries,
                           sf_answers=sf_answers)

    f = io.open(path, 'w', -1, 'utf-8')
    f.write(html)


def count_l(sf_answers, query_id, slot_type):
    count = 0
    for answer in sf_answers:
        output_len = len(answer[query_id].output[slot_type])
        if output_len == 0:
            output_len = 1
        count += output_len

    return count


def empty_system_answer(queries):
    empty_answer = OrderedDict()
    for q in queries:
        empty_answer[q.id] = Answer(q.id, q.entity_type.lower())

    return empty_answer


def str_to_unicode(s):
    return repr(s.decode('unicode-escape'))


def _dict(d, key):
    try:
        return d[key]
    except KeyError:
        return None


def substr(s, beg, end):
    if not s:
        return ''
    return s[beg: end]  # convert s to unicode and return utf-8 substr


def query_snapshot(s, beg, end):
    if s is None:
        return "snapshot not found"
    splitter = [u'.', u'!', u'?', u'。', u'！', u'？']
    target_substr = []
    for spl_upper in splitter:
        for spl_lower in splitter:
            target_substr.append(extract_substring(beg, s[beg: end], spl_upper, spl_lower, s))

    # remove None item
    target_substr = [item for item in target_substr if item is not None]

    return min(target_substr, key=len)[1:].strip()


def is_slt_flr_correct(slot_filler, query_id, slot_type, ldc_answer):
    for line_output in (ldc_answer[query_id].output)[slot_type]:
        if slot_filler == line_output.slot_filler:
            return True
    return False


def eval_development():
    queries = load_sf_query('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/'
                                'tac_kbp_2014_chinese_regular_slot_filling_evaluation_queries.xml')


    eval_result_path = '../../data/result/RPI_mt_response'

    eval_answer = load_ldc_format_answer(eval_result_path)  # {query_id: Answer}

    # check eval_answer
    for q in eval_answer:
        answer = eval_answer[q]
        for s_t in answer.output:
            if not answer.output[s_t]:
                answer.output[s_t] = [LineOutput()]

    tmp = []
    for q in queries:
        if q.id in eval_answer.keys():
            tmp.append(q)
    queries = tmp

    query_dict = OrderedDict()
    for q in queries:
        query_dict[q.id] = q

    src_doc = load_sf_src_doc('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/')

    # check eval_answer docs in src_doc
    docs_to_add = set()
    for q_id in eval_answer.keys():
        for slot_type in eval_answer[q_id].output.keys():
            line_output_list = eval_answer[q_id].output[slot_type]
            for line_output in line_output_list:
                for w_p in line_output.wide_provenance:
                    if w_p.doc_id not in src_doc.keys():
                        docs_to_add.add(w_p.doc_id)
                for s_p in line_output.slot_filler_prov:
                    if s_p.doc_id not in src_doc.keys():
                        docs_to_add.add(s_p.doc_id)

    searcher, analyzer = init_lucene_search()

    docs_added = set()
    for doc_id in docs_to_add:
        correct_doc_index, found_doc_path = search_string(doc_id, searcher, analyzer, 100)
        for i in correct_doc_index:
            if doc_id in found_doc_path[i]:
                f = io.open(found_doc_path[i].replace('/Users/boliangzhang/Desktop/', '/Users/boliangzhang/Documents/Phd/Resources/'), 'r', -1, 'utf-8')
                src_doc[doc_id] = f.read()
                docs_added.add(doc_id)
                break

    doc_not_found = docs_to_add - docs_added

    ldc_answer = eval_answer
    system_answer = empty_system_answer(queries)

    env = Environment(loader=FileSystemLoader(['/Users/boliangzhang/Documents/Phd/Chinese_Slot_Filling/RPISlotFilling/error_analysis/',
                                               '/home/zhangb8/Chinese_Slot_Filling/RPISlotFilling/error_analysis/']))
    env.filters['dict'] = _dict
    env.filters['substr'] = substr
    env.filters['query_snapshot'] = query_snapshot
    env.filters['is_slt_flr_correct'] = is_slt_flr_correct

    template = env.get_template('mainpage.html')

    query_doc_num = OrderedDict()
    for q in queries:
        query_doc_num[q.id] = 5

    html = template.render(slot_types=SLOT_TYPE,
                           ldc_answer=ldc_answer,
                           system_answer=system_answer,
                           queries=query_dict,
                           src_doc=src_doc,
                           query_doc_num=query_doc_num)

    f = io.open('../../data/result/RPI_mt_response.html', 'w', -1, 'utf-8')
    f.write(html)


def main():
    eval_development()


if __name__ == "__main__":
    main()
