#encoding=utf-8
__author__ = 'boliangzhang'

import time
import io
import cPickle
import jianfan
import operator

from collections import OrderedDict
from RPISlotFilling.utils.lucene_search import init_lucene_search
from RPISlotFilling.utils.lucene_search import search
# from RPISlotFilling.src_doc_processing.chinese_sentence_chunking import chinese_sent_tokenizer
from Answer import LineOutput
from Answer import Provenance
# from RPISlotFilling.utils.load_sf_src_doc import load_sf_src_doc
from RPISlotFilling.utils.string_clean import remove_space_linebreak

from Analyzer import Analyzer


class InferenceAnalyzer(Analyzer):
    def __init__(self, query, query_evidences, sf_object):
        Analyzer.__init__(self, query, query_evidences, sf_object)
        self.query_answer = sf_object.final_answers[query.id]

        # load coutry province dict
        self.world_coutry_province = OrderedDict()
        f = io.open('data/dict/china_province_dict', 'r', -1, 'utf-8')
        province_dict = f.read().splitlines()
        self.world_coutry_province[u'中国'] = province_dict

    ########################## person  #########################
    def per_city_of_birth(self, slot_type):
        if not self.query_answer.output[slot_type]:
            return []

        # if stateorprovince is a municipality, city should be emtpy
        try:
            line_output = self.query_answer.output['per:stateorprovince_of_birth'][0]
        except IndexError:
            return self.query_answer.output[slot_type]

        for city in [u'北京', u'重庆', u'天津', u'上海']:
            if city in line_output.slot_filler:
                return []
        return self.query_answer.output[slot_type]

    def per_country_of_birth(self, slot_type):
        return self.country(slot_type, 'per:stateorprovince_of_birth')

    def per_stateorprovince_of_birth(self, slot_type):
        return self.stateorprovince(slot_type, 'per:city_of_birth')

    def per_city_of_death(self, slot_type):
        if not self.query_answer.output:
            return []

        # if stateorprovince is a municipality, city should be emtpy
        try:
            line_output = self.query_answer.output['per:stateorprovince_of_death'][0]
        except IndexError:
            return self.query_answer.output[slot_type]

        for city in [u'北京', u'重庆', u'天津', u'上海']:
            if city in line_output.slot_filler:
                return []

        return self.query_answer.output[slot_type]

    def per_country_of_death(self, slot_type):
        return self.country(slot_type, 'per:stateorprovince_of_death')

    def per_stateorprovince_of_death(self, slot_type):
        return self.stateorprovince(slot_type, 'per:city_of_death')

    def per_countries_of_residence(self, slot_type):
        return self.country(slot_type, 'per:statesorprovinces_of_residence')

    def per_statesorprovinces_of_residence(self, slot_type):
        return self.stateorprovince(slot_type, 'per:cities_of_residence')

    def per_date_of_birth(self, slot_type):
        return self.date(slot_type)

    def per_date_of_death(self, slot_type):
        return self.date(slot_type)

    ######################### organization #########################
    def org_country_of_headquarters(self, slot_type):
        return self.country(slot_type, 'org:stateorprovince_of_headquarters')

    def org_stateorprovince_of_headquarters(self, slot_type):
        return self.stateorprovince(slot_type, 'org:city_of_headquarters')

    def org_members(self, slot_type):
        # if not query_system_answer.output['org:members'][0].slot_filler:
        #     return query_system_answer.output['org:members']
        #
        # result = []
        # member_lineoutput = query_system_answer.output['org:members']
        # top_member_lineoutput = query_system_answer.output['org:top_members_employees']
        # for line_output in member_lineoutput:
        #     if line_output.slot_filler not in [tp_line_output.slot_filler for tp_line_output in top_member_lineoutput]:
        #         result.append(line_output)
        # if not result:
        #     return [LineOutput()]
        # else:
        #     return result
        return []

    def org_top_members_employees(self, slot_type):
        # if not query_system_answer.output['org:top_members_employees'][0].slot_filler:
        #     return query_system_answer.output['org:top_members_employees']
        #
        # line_outputs = query_system_answer.output['org:top_members_employees']
        #
        # similar_output = []
        # for line_output in line_outputs:
        #     tmp = []
        #     for l in line_outputs:
        #         if line_output.slot_filler in l.slot_filler or l.slot_filler in line_output.slot_filler:
        #             tmp.append(l)
        #     similar_output.append(tmp)
        #
        # result = []
        # added_slot_filler = []
        # for element in similar_output:
        #     correct_line_output = sorted(element, key=lambda x: len(x.wide_provenance), reverse=True)[0]
        #     if correct_line_output.slot_filler not in added_slot_filler:
        #         result.append(correct_line_output)
        #         added_slot_filler.append(correct_line_output.slot_filler)
        #
        # return result
        return []

    def org_date_founded(self, slot_type):
        return self.date(slot_type)

    def org_date_dissolved(self, slot_type):
        return self.date(slot_type)

    ########################## utilities #########################
    def country(self, slot_type, evidence_slot_type):
        current_output = self.query_answer.output[slot_type]

        province = None

        # find query's province and city answer.
        for line_output in self.query_answer.output[evidence_slot_type]:
            if line_output.slot_filler:
                province = line_output
        if province is None:
            return current_output

        # infer country by province
        country = ''
        evidence = ''  # evidence is a LineOutput object
        state_slot_filler = jianfan.ftoj(province.slot_filler)
        for c in self.world_coutry_province:
            if state_slot_filler in self.world_coutry_province[c]:
                country = c
                evidence = province
                break

        # if inference fails, return original answer
        if not country:
            return current_output

        # search provenance
        found_doc_path = search(country + state_slot_filler,
                                self.sf_object.lucene_searcher, self.sf_object.lucene_analyzer, 50)

        if not found_doc_path:
            return current_output

        evidence_doc_path = found_doc_path[0]
        # add additional doc to source_doc for visualization
        doc_id = evidence_doc_path.split('/')[-1].strip()
        doc = io.open(evidence_doc_path, 'r', -1, 'utf-8').read()
        self.sf_object.query_docs[doc_id] = doc

        wp_beg = doc.find(country + state_slot_filler)
        wp_end = wp_beg + len(country + state_slot_filler) - 1
        sp_beg = wp_beg + doc[wp_beg:wp_end+1].find(country)
        sp_end = sp_beg + len(country) - 1

        l = LineOutput()
        l.slot_type = slot_type
        l.run_id = self.query_answer.run_id

        p = Provenance()
        p.doc_id = doc_id
        p.beg = wp_beg
        p.end = wp_end
        p.text = country+state_slot_filler
        l.wide_provenance = [p]
        evidence.wide_provenance[0].inference = True
        l.wide_provenance += evidence.wide_provenance  # evidence is a LineOutput object

        l.slot_filler = country

        p = Provenance()
        p.doc_id = doc_id
        p.beg = sp_beg
        p.end = sp_end
        p.text = country
        l.slot_filler_prov = [p]

        l.confidence_score = 1

        # if province is 台湾, coutry should also add 台湾
        if u'台湾' in jianfan.ftoj(province.slot_filler):
            return current_output+[l, province]

        return current_output+[l]

    def stateorprovince(self, slot_type, evidence_slot_type):
        current_output = self.query_answer.output[slot_type]

        city = None

        # find query's city answer.
        for line_output in self.query_answer.output[evidence_slot_type]:
            if line_output.slot_filler:
                city = line_output
        if city is None:
            return current_output

        # infer province by city
        province = ''
        evidence = ''  # evidence is a LineOutput object
        city_slot_filler = city.slot_filler
        city_slot_filler = jianfan.ftoj(city_slot_filler)
        for r in [u'区', u'县', u'市']:
            city_slot_filler = city_slot_filler.replace(r, '')

        for p in self.china_province_city:
            if province:
                break
            if p['type'] == 0:
                if city_slot_filler in [item['name'] for item in p['sub']]:
                    province = p['name']
                    evidence = city
                    break
            else:
                for c in p['sub']:
                    if city_slot_filler in [item['name'] for item in c['sub']]:
                        province = p['name']
                        evidence = city
                        break

        # if inference fails, return original answer
        if not province:
            return current_output

        # search provenance
        found_doc_path = search(province + city_slot_filler, self.searcher, self.analyzer, 50)

        if not found_doc_path:
            return current_output

        evidence_doc_path = found_doc_path[0]
        # add additional doc to source_doc for visualization
        doc_id = evidence_doc_path.split('/')[-1].strip()
        doc = io.open(evidence_doc_path, 'r', -1, 'utf-8').read()
        self.sf_object.query_docs[doc_id] = doc

        wp_beg = doc.find(province + city_slot_filler)
        wp_end = wp_beg + len(province + city_slot_filler) - 1
        sp_beg = wp_beg + doc[wp_beg:wp_end+1].find(province)
        sp_end = sp_beg + len(province) - 1

        l = LineOutput()
        l.slot_type = slot_type
        l.run_id = self.query_answer.run_id

        p = Provenance()
        p.doc_id = doc_id
        p.beg = wp_beg
        p.end = wp_end
        p.text = province+city_slot_filler
        l.wide_provenance = [p]
        evidence.wide_provenance[0].inference = True
        l.wide_provenance += evidence.wide_provenance  # evidence is a LineOutput object

        l.slot_filler = province

        p = Provenance()
        p.doc_id = doc_id
        p.beg = sp_beg
        p.end = sp_end
        p.text = province
        l.slot_filler_prov = [p]

        l.confidence_score = 1

        return current_output+[l]

    #
    # def add_evidence(evidence_doc_path, version):
    #     f = io.open(evidence_doc_path, 'r', -1, 'utf-8').read()
    #     doc_id = evidence_doc_path.split('/')[-1].strip()
    #     if version == 'ldc':
    #         f_out = io.open('../../data/LDC/LDC2014E123_TAC_KBP_2014_Chinese_Regular_Slot_Filling_Training_Data/'
    #                         'data/source_doc/support_doc/' + doc_id, 'w', -1, 'utf-8')
    #         f_out.write(f)
    #     elif version == 'eval':
    #         f_out = io.open('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/'
    #                         '/source_doc/support_doc/' + doc_id, 'w', -1, 'utf-8')
    #         f_out.write(f)

    def general_inference(query_system_answer):
        # load sf source document
        if version == 'ldc':
            src_doc = load_sf_src_doc('../../data/LDC/LDC2014E123_TAC_KBP_2014_Chinese_Regular_Slot_Filling_Training_Data/'
                                      'data/source_doc/')
        elif version == 'eval':
            src_doc = load_sf_src_doc('../../data/LDC/KBP_2015_Chinese_Regular_Slot_Filling_Evaluation_Data/source_doc/')

        # ================== remove slot filler related to 记者 ===================== #
        for slot_type in query_system_answer.output.keys():
            line_outputs = query_system_answer.output[slot_type]

            corrected_line_outputs = []
            for l in line_outputs:
                if not l.slot_filler:
                    corrected_line_outputs.append(l)
                    continue
                void_l = False
                for w_p in l.wide_provenance:
                    w_p_text = src_doc[w_p.doc_id][w_p.beg:w_p.end]
                    if (u'记者' + l.slot_filler) in w_p_text or (l.slot_filler + u'记者') in w_p_text:
                        void_l = True
                        break
                if void_l is False:
                    corrected_line_outputs.append(l)

            query_system_answer.output[slot_type] = corrected_line_outputs

        # ================== fix slot filler offset ===================== #
        for slot_type in query_system_answer.output.keys():
            if 'date' in slot_type:
                continue

            line_outputs = query_system_answer.output[slot_type]

            for l in line_outputs:
                if not l.slot_filler:
                    continue
                for i in xrange(len(l.slot_filler_prov)):
                    try:
                        s_p = l.slot_filler_prov[i]
                        s_p_text = src_doc[s_p.doc_id][s_p.beg:s_p.end+1]
                        if l.slot_filler == remove_space_linebreak(s_p_text):
                            continue
                        w_p = l.wide_provenance[i]
                        w_p_text = src_doc[w_p.doc_id][w_p.beg:w_p.end+1]

                        correct_w_p_index = src_doc[w_p.doc_id].find(w_p_text)
                        s_p_inner_index = w_p_text.find(l.slot_filler)
                        correct_s_p_beg = correct_w_p_index + s_p_inner_index
                        correct_s_p_end = correct_s_p_beg + len(l.slot_filler) - 1

                        corrected_s_p_text = src_doc[s_p.doc_id][correct_s_p_beg:correct_s_p_end+1]
                        if corrected_s_p_text != l.slot_filler:
                            continue

                        l.slot_filler_prov[i].beg = correct_s_p_beg
                        l.slot_filler_prov[i].end = correct_s_p_end
                    except IndexError:
                        continue

        return query_system_answer

    def date(self, slot_type):
        line_outputs = self.query_answer.output[slot_type]

        if not line_outputs:
            return []

        year_count = dict()
        for l in line_outputs:
            year = l.slot_filler.split('-')[0]
            try:
                year_count[year] += 1
            except KeyError:
                year_count[year] = 1

        correct_year = sorted(year_count.items(), key=operator.itemgetter(1), reverse=True)[0][0]

        result = ''
        min_xx_count = 3
        for l in line_outputs:
            if correct_year not in l.slot_filler:
                continue

            xx_count = l.slot_filler.count('XX')

            if xx_count < min_xx_count:
                result = l
                min_xx_count = xx_count

        return [result]








# def inference(query_evidence, offset_mapping, system_answer, v):
#     global version
#     version = v
#
#     global cleaned_doc_offset_mapping
#     cleaned_doc_offset_mapping = offset_mapping
#
#     # load china province list
#     global world_coutry_province
#     world_coutry_province = OrderedDict()
#     province_dict = []
#     f = io.open('../../data/dict/china_province_dict', 'r', -1, 'utf-8')
#     for line in f:
#         province_dict.append(line.strip())
#     world_coutry_province[u'中国'] = province_dict
#
#     global searcher, analyzer
#     searcher, analyzer = init_lucene_search()
#
#     # load china province city list
#     global china_province_city
#     china_province_city = cPickle.load(open('../../data/dict/china_province_city.pkl', 'rb'))
#
#     for query in query_evidence:
#         evidence = query_evidence[query]
#
#         query_system_answer = system_answer[query.id]
#
#         # inference
#         query_answer = query_inference(self, slot_type)
#
#         system_answer[query.id] = query_answer
#
#     return system_answer
#
#
# def query_inference(self, slot_type):
#     # dispatcher is a OrderedDict of dp analysis function for each slot type
#     per_dispatcher = OrderedDict([('per:alternate_names', per_alternate_names),
#                                   ("per:city_of_birth", per_city_of_birth),
#                                   ("per:stateorprovince_of_birth", per_stateorprovince_of_birth),  # require first do province inference, and then country
#                                   ("per:country_of_birth", per_country_of_birth),
#                                   ("per:city_of_death", per_city_of_death),
#                                   ("per:stateorprovince_of_death", per_stateorprovince_of_death),
#                                   ("per:country_of_death", per_country_of_death),
#                                   ("per:statesorprovinces_of_residence", per_statesorprovinces_of_residence),
#                                   ("per:countries_of_residence", per_countries_of_residence),
#                                   ("per:date_of_birth", per_date_of_birth),
#                                   ("per:date_of_death", per_date_of_death)
#                                   ])
#
#     org_dispatcher = OrderedDict([("org:country_of_headquarters", org_country_of_headquarters),
#                                   ("org:stateorprovince_of_headquarters", org_stateorprovince_of_headquarters),
#                                   ("org:members", org_members),
#                                   ("org:top_members_employees", org_top_members_employees),
#                                   ("org:date_founded", org_date_founded),
#                                   ("org:date_dissolved", org_date_dissolved)
#                                   ])
#
#     if query.entity_type == 'PER':
#         dispatcher = per_dispatcher
#     elif query.entity_type == 'ORG':
#         dispatcher = org_dispatcher
#
#     for slot_type in dispatcher.keys():
#         # inference by slot type
#         try:
#             slot_type_evidence = evidence[slot_type]
#         except KeyError:
#             slot_type_evidence = None
#
#         slot_type_line_outputs = dispatcher[slot_type](query, slot_type_evidence, query_system_answer)
#
#         query_system_answer.output[slot_type] = slot_type_line_outputs
#
#     # general inference for all answers, like remove answers near 记者, fix slot filler offset error
#     query_system_answer = general_inference(query_system_answer)
#     return query_system_answer
#
#
#





