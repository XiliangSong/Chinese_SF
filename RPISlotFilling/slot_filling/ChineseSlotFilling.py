#encoding=utf-8
__author__ = 'boliangzhang'


import os
import lucene
import io
import sys
import jianfan
import cPickle
import time
import shutil
import multiprocessing
from xml.etree import ElementTree as ET
from collections import OrderedDict

from RPISlotFilling.lib.corenlp.corenlp import batch_parse
from RPISlotFilling.utils.stanford_corenlp import stanford_parser

from Query import Query
from Answer import Answer
from Evidence import Evidence
from DependencyAnalyzer import DependencyAnalyzer
from PatternAnalyzer import PatternAnalyzer
from InferenceAnalyzer import InferenceAnalyzer
from RPISlotFilling.utils.string_clean import remove_xml_tag, remove_space_linebreak, remove_doc_noise
from RPISlotFilling.visualization.visualizer import visualizer
from RPISlotFilling.utils.lucene_search import init_lucene_search
from RPISlotFilling.utils.lucene_search import search


class ChineseSlotFilling(object):
    # constant
    PER_SLOT_TYPE = ["per:alternate_names", "per:date_of_birth", "per:age", "per:country_of_birth",
                     "per:stateorprovince_of_birth", "per:city_of_birth", "per:origin", "per:date_of_death",
                     "per:country_of_death", "per:stateorprovince_of_death", "per:city_of_death",
                     "per:cause_of_death", "per:countries_of_residence", "per:statesorprovinces_of_residence",
                     "per:cities_of_residence", "per:schools_attended", "per:title", "per:title",
                     "per:employee_or_member_of", "per:employee_or_member_of", "per:religion",
                     "per:spouse", "per:children", "per:parents", "per:siblings", "per:other_family", "per:charges"]

    ORG_SLOT_TYPE = ["org:alternate_names", "org:political_religious_affiliation", "org:top_members_employees",
                     "org:number_of_employees_members", "org:members", "org:member_of", "org:subsidiaries",
                     "org:parents", "org:founded_by", "org:date_founded", "org:date_dissolved",
                     "org:country_of_headquarters", "org:stateorprovince_of_headquarters",
                     "org:city_of_headquarters", "org:shareholders", "org:website"]

    def __init__(self):
        print('==================== RPI BLENDER Chinese Slot Filling ========================\n')
        print('* initializing...')
        self.queries = None
        self.triggers = None
        self.query_docs = dict()
        self.cleaned_docs = dict()  # {doc_id: doc}
        self.segmented_docs = dict()
        self.doc_mapping_table = dict()
        self.evidence = None

        self.CN_SF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')
        os.chdir(self.CN_SF_PATH)

        # initialize stanford corenlp
        os.environ['STANFORD_PARSER'] = os.path.abspath('externals/stanford-parser-full-2014-01-04/')
        os.environ['STANFORD_MODELS'] = os.path.abspath('externals/stanford-parser-full-2014-01-04/')

        self.final_answers = OrderedDict()

        self.lucene_searcher, self.lucene_analyzer = init_lucene_search()

    # load standard LDC query file
    def load_query(self, path):
        self.queries = []
        root = ET.parse(path)
        for query in root.findall('query'):
            q = Query(query)
            self.queries.append(q)

        # initialize empty answer
        for q in self.queries:
            self.final_answers[q.id] = Answer(q)

    def initialize_answer(self):
        for q in self.queries:
            self.final_answers[q.id] = Answer(q)

    def load_triggers(self, path):
        per_trigger_mapping = {'per_death': ['per:date_of_death', 'per:country_of_death',
                                             'per:stateorprovince_of_death', 'per:city_of_death'],
                               'per_birth': ['per:date_of_birth', 'per:country_of_birth',
                                             'per:stateorprovince_of_birth', 'per:city_of_birth'],
                               'per_residence': ['per:countries_of_residence', 'per:statesorprovinces_of_residence',
                                                 'per:cities_of_residence']
                               }

        org_trigger_mapping = {'org_headquarters': ['org:country_of_headquarters', 'org:stateorprovince_of_headquarters',
                                                    'org:city_of_headquarters'],
                               'org_parentchildren': ['org:parents', 'org:subsidiaries']
                               }

        per_dict = dict()
        org_dict = dict()

        for s in self.PER_SLOT_TYPE:
            for key in per_trigger_mapping:
                if s in per_trigger_mapping[key]:
                    fnm = key
                    break
                else:
                    fnm = s
            fnm = fnm.replace(':', '_')
            f = io.open(os.path.join(path, fnm + '.txt'), 'r', -1, 'utf-8')
            per_dict[s] = set(f.read().strip().split('\n'))

        for s in self.ORG_SLOT_TYPE:
            for key in org_trigger_mapping:
                if s in org_trigger_mapping[key]:
                    fnm = key
                    break
                else:
                    fnm = s
            fnm = fnm.replace(':', '_')
            f = io.open(os.path.join(path, fnm + '.txt'), 'r', -1, 'utf-8')
            org_dict[s] = set(f.read().strip().split('\n'))

        self.triggers = {'PER': per_dict, 'ORG': org_dict}

    def retrieve_query_doc(self):
        for q in self.queries:
            q_results = dict()
            print(q.name + '...'),
            found_doc_path = search(q.name, self.lucene_searcher, self.lucene_analyzer, 3000)
            for doc_path in found_doc_path:
                doc_id = doc_path.split('/')[-1].strip()
                doc_content = io.open(doc_path, 'r', -1, 'utf-8').read()
                if doc_content.replace(' ', '').replace('\n', '').count(q.name) < 4:
                    continue
                q_results[doc_id] = doc_content

                # clean doc
                cleaned_doc = remove_doc_noise(doc_content)  # remove tags like datetime, headline, dateline, etc.
                cleaned_doc = remove_xml_tag(cleaned_doc)
                cleaned_doc = remove_space_linebreak(cleaned_doc)

                # create offset mapping table betwenn clean doc and origin doc
                if doc_id in self.doc_mapping_table.keys():
                    continue
                offset_mapping_table = OrderedDict()
                cleaned_doc_index = 0
                origin_doc_index = 0
                for char in cleaned_doc:
                    while True:
                        if char != doc_content[origin_doc_index]:
                            origin_doc_index += 1
                        else:
                            offset_mapping_table[cleaned_doc_index] = origin_doc_index
                            cleaned_doc_index += 1
                            origin_doc_index += 1
                            break
                # check correctness of offset mapping table
                for index in offset_mapping_table.keys():
                    assert cleaned_doc[index] == doc_content[offset_mapping_table[index]]

                self.doc_mapping_table[doc_id] = offset_mapping_table
                self.cleaned_docs[doc_id] = cleaned_doc

            self.query_docs[q.id] = q_results

            print('Done')

    # evidences are the sentences that contain both query and trigger word of each slot type
    def evidence_extaction(self):
        # ************* batch segment long article ************* #
        start = time.time()
        if os.path.exists('data/.tmp/'):
            shutil.rmtree('data/.tmp')
        os.makedirs('data/.tmp/')  # create a temperal dir for parsing large paragraphs
        for doc_id in self.cleaned_docs:
            f = io.open(os.path.join('data/.tmp', doc_id), 'w', -1, 'utf-8')
            f.write(self.cleaned_docs[doc_id])
            f.close()

        # run stanford segmenter
        stanford_nlp_dir = os.path.join(self.CN_SF_PATH,
                                        'externals/stanford-corenlp-full-2014-08-27/')
        segmenter_result = list(batch_parse('data/.tmp/',
                                            stanford_nlp_dir,
                                            properties=os.path.join(stanford_nlp_dir,
                                                                    "StanfordCoreNLP-chinese.Segmenter.properties")
                                            ))
        for r in segmenter_result:
            self.segmented_docs[r['file_name']] = r['sentences']
        print('segmenting time cost '+str(time.time()-start))

        # cpickle for development
        # cPickle.dump(self.segmented_docs, open('data/segmented_docs.pkl', 'wb'))
        # self.segmented_docs = cPickle.load(open('data/segmented_docs.pkl', 'rb'))

        # ************* select evidence ************* #
        sent_to_parse = dict()

        self.evidence = OrderedDict()
        for query in self.queries:
            print('\textracting ' + query.name)

            evidences = OrderedDict()  # {slot_type: sentence_parsed_result}
            for doc_id in self.query_docs[query.id].keys():
                seg_result = self.segmented_docs[doc_id]
                for i in xrange(len(seg_result)):  # sentence is stanford standard format output
                    sentence = seg_result[i]
                    sent_id = '|'.join([doc_id, str(i)])
                    # if sentence is too long or too short, it carries less dependency information
                    if len(sentence['words']) > 130 or len(sentence['words']) < 3:
                        continue

                    sent_text = ''.join(sentence['text'])

                    # *************** check if this sentence is an evidence ******************** #
                    # ============== common case ============= #
                    seg_sent_text = sentence['text']  # list of tokens
                    seg_sent_text = [jianfan.ftoj(w) for w in seg_sent_text]

                    # here joining s['text'] list will overcome segmentation errors
                    if query.name not in ''.join(seg_sent_text):
                        continue

                    triggers = self.triggers[query.entity_type]

                    if query.entity_type == 'PER':
                        slot_types = self.PER_SLOT_TYPE
                    elif query.entity_type == 'ORG':
                        slot_types = self.ORG_SLOT_TYPE

                    for slot_type in slot_types:
                        if slot_type not in evidences.keys():
                            evidences[slot_type] = []
                        for t in triggers[slot_type]:
                            # compare triggers to words by segmentation, might affected by segmentation errors
                            if t not in seg_sent_text:
                                continue
                            evidences[slot_type].append(Evidence(doc_id, query.id, t, sent_text, sent_id))
                            sent_to_parse[sent_id] = sent_text  # add sentence and do parallel parsing later.

                    # ============== special case ============== #
                    if query.entity_type == 'PER':
                        evidences['per:alternate_names'].append(Evidence(doc_id, query.id, '',
                                                                         sent_text, sent_id, sentence))

                    if query.entity_type == 'ORG':
                        # for org:alternate_names, the article contains the query is evidence, for pattern match
                        evidences['org:alternate_names'].append(Evidence(doc_id, query.id, '',
                                                                         sent_text, sent_id, sentence))

                        # for org:XXX_headquarters, the article contains the query is evidence, for pattern match
                        evidences['org:country_of_headquarters'].append((Evidence(doc_id, query.id, '',
                                                                                  sent_text, sent_id, sentence)))
                        evidences['org:stateorprovince_of_headquarters'].append((Evidence(doc_id, query.id, '',
                                                                                          sent_text, sent_id, sentence)))
                        evidences['org:city_of_headquarters'].append((Evidence(doc_id, query.id, '',
                                                                               sent_text, sent_id, sentence)))

            self.evidence[query.id] = evidences

        # *************** parallel parsing ****************** #
        def chunkIt(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg

            return out

        # run stanford parser in multiprocessing
        process_num = multiprocessing.cpu_count() / 2 if multiprocessing.cpu_count() / 2 < 10 else 10
        p = multiprocessing.Pool(processes=process_num)
        chunked_sent = [dict(item) for item in chunkIt(sent_to_parse.items(), process_num)]
        mp_result = [p.apply_async(stanford_parser,
                                   args=(chunked_sent[i], str(i))) for i in range(process_num)]
        mp_result = [p.get() for p in mp_result]
        sent_parsing_result = {}
        for r in mp_result:
            sent_parsing_result.update(r)

        # cpickle for development
        # cPickle.dump(sent_parsing_result, open('data/sent_parsing_result.pkl', 'wb'))
        # sent_parsing_result = cPickle.load(open('data/sent_parsing_result.pkl', 'rb'))

        # updating evidences
        for q_id in self.evidence.keys():
            evidences = self.evidence[q_id]
            for slot_type in evidences.keys():
                for e in evidences[slot_type]:
                    if not e.trigger:
                        continue
                    e.parse_result = sent_parsing_result[e.sent_id]

        # *************** correct segmenter error ******************** #
        china_province_city = cPickle.load(open('data/dict/china_province_city.pkl', 'rb'))
        province_city_list = []
        for p in china_province_city:
            province_city_list += [p['name']]
            for c in p['sub']:
                province_city_list += [c['name']]
                if p['type'] == 0:
                    continue
                for d in c['sub']:
                    province_city_list += [d['name']]

        for q_id in self.evidence.keys():
            for slot_type in self.evidence[q_id]:
                for i in xrange(len(self.evidence[q_id][slot_type])):
                    self.evidence[q_id][slot_type][i] = self.correct_evidence(self.find_query(q_id).name,
                                                                              self.evidence[q_id][slot_type][i])
                    for p_or_c in province_city_list:
                        if len(p_or_c) > 2 and p_or_c in \
                                ''.join(self.evidence[q_id][slot_type][i].parse_result['text']):
                            self.evidence[q_id][slot_type][i] = \
                                self.correct_evidence(p_or_c, self.evidence[q_id][slot_type][i])

        print('Done')

    def evidence_visualization(self):
        return

    def find_query(self, query_id):
        for q in self.queries:
            if q.id == query_id:
                return q
        return None

    def correct_evidence(self, string, evidence):
        parse_result = evidence.parse_result

        # get index of item that need to combine
        p1 = 0
        text = parse_result['text']
        index_to_combine = []
        while p1 < len(text):
            if string == text[p1]:
                p1 += 1
            elif string.startswith(text[p1]):
                p2 = p1 + 1
                while len(''.join(text[p1:p2])) <= len(string) and p2 <= len(text):
                    if ''.join(text[p1:p2]) == string:
                        index_to_combine.append((p1, p2))
                        break
                    p2 += 1
                p1 = p2
            else:
                p1 += 1

        # correct 'text'
        if len(index_to_combine) > 0:
            new_text = []
            new_text += text[:index_to_combine[0][0]]
            for i in xrange(len(index_to_combine)):
                combined_text = ''.join(text[index_to_combine[i][0]: index_to_combine[i][1]])
                if i == len(index_to_combine) - 1:
                    new_text += [combined_text] + text[index_to_combine[i][1]:]
                else:
                    new_text += [combined_text] + text[index_to_combine[i][1]: index_to_combine[i+1][0]]
        else:
            new_text = text

        # correct 'words'
        words = parse_result['words']
        if len(index_to_combine) > 0:
            new_words = []
            new_words += words[:index_to_combine[0][0]]
            for i in xrange(len(index_to_combine)):
                combined_word = [string, OrderedDict()]
                combined_word[1]['CharacterOffsetBegin'] = words[index_to_combine[i][0]][1]['CharacterOffsetBegin']
                combined_word[1]['CharacterOffsetEnd'] = words[index_to_combine[i][1]-1][1]['CharacterOffsetEnd']
                combined_word[1]['NamedEntityTag'] = self.find_query(evidence.query_id).entity_type
                combined_word[1]['PartOfSpeech'] = 'NN'
                if i == len(index_to_combine) - 1:
                    new_words += [combined_word] + words[index_to_combine[i][1]:]
                else:
                    new_words += [combined_word] + words[index_to_combine[i][1]: index_to_combine[i+1][0]]
        else:
            new_words = words

        # create mapping between old text or word index
        mapping = dict()
        new_text_index = 0
        for i in xrange(len(text)):
            index_mapped = False
            for item in index_to_combine:
                if i in range(item[0], item[1]):
                    mapping[i] = new_text_index
                    index_mapped = True
                    if i == item[-1]-1:
                        new_text_index += 1
                    break
            if index_mapped is False:
                mapping[i] = new_text_index
                new_text_index += 1
        mapping[-1] = -1

        # modify dp path based on mapping
        new_dp = []
        if 'dependencies' in parse_result.keys():
            dep_path = parse_result['dependencies']
            if dep_path:  # if dep path is not empty
                index_to_map = []
                for item in index_to_combine:
                    index_to_map += range(item[0], item[1])
                for triple in dep_path:
                    arg1 = '-'.join(triple[1].split('-')[:-1])
                    arg2 = '-'.join(triple[2].split('-')[:-1])
                    arg1_index = int(triple[1].split('-')[-1]) - 1
                    arg2_index = int(triple[2].split('-')[-1]) - 1
                    arg1_index_mapped = mapping[arg1_index] + 1
                    arg2_index_mapped = mapping[arg2_index] + 1
                    if arg1_index_mapped == arg2_index_mapped:
                        continue
                    if arg1_index in index_to_map:
                        arg1 = string
                    if arg2_index in index_to_map:
                        arg2 = string
                    new_dp += [[triple[0], arg1 + '-' + str(arg1_index_mapped), arg2 + '-' + str(arg2_index_mapped)]]

        new_parse_result = {'text': new_text, 'words': new_words, 'dependencies': new_dp}

        new_evidence = Evidence(evidence.doc_id, evidence.query_id, evidence.trigger,
                                evidence.sent_text, evidence.sent_id, new_parse_result)

        return new_evidence

    def dp_analyzer(self):
        for q in self.queries:
            q_evidence = self.evidence[q.id]
            dp_analyzer = DependencyAnalyzer(q, q_evidence, self)

            query_answer = self.final_answers[q.id]

            dp_answer = dp_analyzer.get_answer(query_answer)

            self.final_answers[q.id] = dp_answer

    def pm_analyzer(self):
        for q in self.queries:
            q_evidence = self.evidence[q.id]
            pm_analyzer = PatternAnalyzer(q, q_evidence, self)

            query_answer = self.final_answers[q.id]

            pm_answer = pm_analyzer.get_answer(query_answer)

            self.final_answers[q.id] = pm_answer

    def inf_analyzer(self):
        for q in self.queries:
            q_evidence = self.evidence[q.id]
            inf_analyzer = InferenceAnalyzer(q, q_evidence, self)

            query_answer = self.final_answers[q.id]

            inf_answer = inf_analyzer.get_answer(query_answer)

            self.final_answers[q.id] = inf_answer

    def answer_clean_up(self):
        for answer in self.final_answers.values():
            for slot_type in answer.output.keys():
                line_outputs = answer.output[slot_type]
                if not line_outputs:
                    continue

                unique_slot_filler = dict()
                for line_output in line_outputs:
                    try:
                        unique_slot_filler[line_output.slot_filler].append(line_output)
                    except KeyError:
                        unique_slot_filler[line_output.slot_filler] = [line_output]

                result = []
                for slot_filler in unique_slot_filler:
                    for line_output in unique_slot_filler[slot_filler]:
                        if len(line_output.wide_provenance) > 1:
                            result.append(line_output)
                            break
                    else:
                        result.append(unique_slot_filler[slot_filler][0])

                line_outputs = result
                if slot_type not in ["per:alternate_names", "per:origin", "per:countries_of_residence",
                                     "per:statesorprovinces_of_residence", "per:cities_of_residence",
                                     "per:schools_attended", "per:title", "per:employee_or_member_of",
                                     "per:children", "per:parents", "per:siblings", "per:other_family",
                                     "org:alternate_names", "org:top_members_employees", "org:subsidiaries",
                                     "org:parents", "org:founded_by", "org:shareholders"]:
                    for line_output in line_outputs:
                        if len(line_output.wide_provenance) > 1:
                            line_outputs = [line_output]
                            break
                    else:
                        line_outputs = line_outputs[:1]

                answer.output[slot_type] = line_outputs

    def get_answer(self, query_file_path):
        # load queries
        self.load_query(query_file_path)

        # load triggers
        self.load_triggers('data/triggers')

        # retrieve query docs
        self.retrieve_query_doc()

        # evidence extraction
        self.evidence_extaction()

        # dependency path analyzer
        self.dp_analyzer()

        # pattern match analyzer
        self.pm_analyzer()

        # infer answers by other slot type answers
        self.inf_analyzer()

        # answer clean up
        self.answer_clean_up()

        return self.final_answers

    def export_answer(self, path):
        f = io.open(path, 'w', -1, 'utf-8')
        export_text = []
        for query_id in self.final_answers.keys():
            query = self.find_query(query_id)
            answer = self.final_answers[query_id]
            if query.entity_type == "PER":
                slot_type_list = self.PER_SLOT_TYPE
            elif query.entity_type == "ORG":
                slot_type_list = self.ORG_SLOT_TYPE

            for slot_type in slot_type_list:
                line_outputs = answer.output[slot_type]

                if not line_outputs:
                    export_line = [query_id, slot_type, answer.run_id]
                    export_line.append('NIL')
                    export_text.append('\t'.join(export_line))
                    continue

                for l in line_outputs:
                    export_line = [query_id, slot_type, answer.run_id]
                    w_p_export = []
                    w_p_scope = []
                    for w_p in l.wide_provenance[:4]:
                        if w_p.end - w_p.beg > 130:  # wide provenance length should be less than 210
                            continue
                        w_p_scope.append((w_p.doc_id, w_p.beg, w_p.end))
                        w_p_export.append(w_p.doc_id + ':' + str(w_p.beg) + '-' + str(w_p.end))

                    s_p_export = []
                    for s_p in l.slot_filler_prov:
                        for w in w_p_scope:
                            if s_p.doc_id == w[0] and s_p.beg >= w[1] and s_p.end <= w[2]:
                                s_p_export.append(s_p.doc_id + ':' + str(s_p.beg) + '-' + str(s_p.end))
                                break
                        if s_p_export:
                            break
                    export_line += [','.join(w_p_export), l.slot_filler,
                                    ','.join(s_p_export), str(l.confidence_score)]

                    if len(w_p_export) > 0 and len(s_p_export) > 0:
                        export_text.append('\t'.join(export_line))

        f.write('\n'.join(export_text))

        f.close()

    def visualize(self, path):
        for answer in self.final_answers.values():
            answer.generate_html_str()

        visualizer(self.queries, [self.final_answers], path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Incorrect number of arguments.')
        print('ChineseSlotFilling requires 2 arguments:')
        print('\t1) KBP format slot filling queries.')
        print('\t2) Path to output result and visualization result.')
        exit()

    valid_path = True

    query_path = os.path.join(os.getcwd(), sys.argv[1])
    if not os.path.exists(query_path):
        print(query_path+' not exist')
        valid_path = False

    output_path = os.path.join(os.getcwd(), sys.argv[2])
    if not os.path.exists(output_path):
        print(output_path+' not exist')
        valid_path = False

    if not valid_path:
        sys.exit()

    cn_sf = ChineseSlotFilling()

    cn_sf.get_answer(query_path)

    cn_sf.export_answer(os.path.join(output_path, 'cn_sf_result.tab'))

    cn_sf.visualize(os.path.join(output_path, 'cn_sf_result.html'))





