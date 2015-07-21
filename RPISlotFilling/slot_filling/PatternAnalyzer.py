#encoding=utf-8
__author__ = 'boliangzhang'


import io
import cPickle
import Levenshtein
import itertools
import jianfan

from Analyzer import Analyzer

class PatternAnalyzer(Analyzer):
    def __init__(self, query, query_evidences, sf_object):
        Analyzer.__init__(self, query, query_evidences, sf_object)

    ########################## person #########################
    def per_alternate_names(self, slot_type):
        # find all sublist that between element beg and end, it's used for searching names in quotion mark.
        # return list of tuples (h, t), h is the head index of substring and t is the tail index of substring
        def iter_find_sublist(beg, end, l, i=0):
            sublist = []
            for i in xrange(i, len(l)):
                if l[i] == beg:
                    beg_index = i
                    for j in xrange(5):
                        i += 1
                        if i >= len(l):
                            break
                        if l[i] == end:
                            end_index = i
                            sublist.append((beg_index, end_index))
                            if i < len(l)-1:
                                sublist += iter_find_sublist(beg, end, l, i+1)
                            break
                    break

            return sublist

        line_outputs = []

        for e in self.evidences[slot_type]:
            query_index = [i for i, x in enumerate(e.parse_result['text']) if x == self.query.name]
            quoted_string_index = iter_find_sublist(u'“', u"”", e.parse_result['text'])
            quoted_string_index += iter_find_sublist(u'"', u'"', e.parse_result['text'])
            quoted_string_index += iter_find_sublist(u"‘", u"’", e.parse_result['text'])
            quoted_string_index += iter_find_sublist(u"'", u"'", e.parse_result['text'])

            for qtd_i in quoted_string_index:
                for qry_i in query_index:
                    if 0 < qry_i - qtd_i[1] < 2:
                        valid_name = True
                        for word in e.parse_result['words'][qtd_i[0]+1:qtd_i[1]]:
                            if word[1]['PartOfSpeech'] == 'VV':  # verb in entity is not an alternate name
                                valid_name = False
                                break
                        if valid_name is False:
                            continue

                        slot_filler = ''.join(e.parse_result['text'][qtd_i[0]+1:qtd_i[1]])

                        l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                        # ================ post filtering ================= #
                        if l.slot_filler in [u'三十而立']:
                            continue

                        line_outputs.append(l)

        return line_outputs

    def per_spouse(self, slot_type):
        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger = e.trigger
            query_index = [i for i, x in enumerate(e.parse_result['text']) if x == self.query.name]
            trigger_index = [i for i, x in enumerate(e.parse_result['text']) if x == trigger]
            per_entity_index = [i for i, x in enumerate(e.parse_result['words']) if x[1]['NamedEntityTag'] == 'PERSON']
            spouse_entity_index = []
            for q_i in query_index:
                for p_i in per_entity_index:
                    for t_i in trigger_index:
                        distance = 3
                        if q_i < t_i < p_i and p_i - q_i <= distance:
                            spouse_entity_index.append(p_i)
                        elif p_i < t_i < q_i and q_i - p_i <= distance:
                            spouse_entity_index.append(p_i)

            if len(spouse_entity_index) == 0:
                continue

            for i in spouse_entity_index:
                slot_filler = e.parse_result['text'][i]
                l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                line_outputs.append(l)

        return line_outputs

    ########################## organization #########################
    def org_alternate_names(self, slot_type):
        # load china province city list
        china_province_city = cPickle.load(open('data/dict/china_province_city.pkl', 'rb'))
        city_list = []
        for p in china_province_city:
            if p['type'] == 0 and p['name'] != (u'台湾' or u'臺灣'):  # type 0 means 直辖市
                continue
            for c in p['sub']:
                city_list.append(c['name'])
                if p['name'] == (u'台湾' or u'臺灣'):
                    continue
                for d in c['sub']:
                    city_list.append(d['name'])

        # load china province list
        province_dict = []
        f = io.open('data/dict/china_province_dict', 'r', -1, 'utf-8')
        for line in f:
            province_dict.append(line.strip())

        # load country list
        country_list = []
        f = io.open('data/dict/country_list', 'r', -1, 'utf-8')
        for line in f:
            country_list.append(line.strip())

        line_outputs = []
        # find query name segmentation
        query_name_seg = []
        for e in self.evidences[slot_type]:
            if self.query.name not in ''.join(e.parse_result['text']):
                continue
            org_list = self.find_org(e.parse_result['words'])

            for org in org_list:
                if self.query.name in ''.join([word[0] for word in org]):
                    query_name_seg = org

        for e in self.evidences[slot_type]:
            org_list = self.find_org(e.parse_result['words'])
            alternate_name = []
            for org in org_list:
                org_name = ''.join([w[0] for w in org])
                if org_name == self.query.name:
                    continue

                # ======================== organization name pattern match ======================= #
                # edit distance
                simi_score = Levenshtein.distance(self.query.name, org_name)
                if simi_score < 2:
                    alternate_name.append(org)
                    continue

                # alternate name must consist of words from query name
                if set(org_name) - set(self.query.name):
                    continue

                # org name should not be the name of a single city, country or state/province
                def foo():
                    for element in list(itertools.chain(city_list, province_dict, country_list)):
                        if org_name in element:
                            return False
                    return True
                if not foo():
                    continue

                # abbreviation match
                query_name_abbre = ''.join(w[0][0] for w in query_name_seg)
                if query_name_abbre in org_name or org_name in query_name_abbre:
                    alternate_name.append(org)
                    continue

                # jaro_winkler score: the closer the word to the beginning, the higher weight it has.
                simi_score = Levenshtein.jaro_winkler(self.query.name, org_name)
                if simi_score > 0.8:
                    alternate_name.append(org)
                    continue

            for org in alternate_name:
                slot_filler = ''.join([w[0] for w in org])
                l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                line_outputs.append(l)

        return line_outputs

    def org_subsidiaries(self, slot_type):
        line_outputs = []

        f = io.open('data/triggers/org_parentchildren.txt', 'r', -1, 'utf-8')
        trigger_word = []
        for line in f:
            trigger_word.append(line.strip())

        for e in self.evidences[slot_type]:
            org_list = self.find_org(e.parse_result['words'])
            for org in org_list:
                org_name = ''.join([w[0] for w in org])
                if self.query.name not in org_name or self.query.name == org_name:
                    continue
                for t in trigger_word:
                    if t in org_name:
                        slot_filler = ''.join([w[0] for w in org])
                        l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                        line_outputs.append(l)

        return line_outputs

    def org_country_of_headquarters(self, slot_type):
        line_outputs = self.org_headquarters(slot_type)
        return line_outputs

    def org_stateorprovince_of_headquarters(self, slot_type):
        line_outputs = self.org_headquarters(slot_type)
        return line_outputs

    def org_city_of_headquarters(self, slot_type):
        line_outputs = self.org_headquarters(slot_type)
        return line_outputs

    ########################## utilities #########################
    def find_org(self, word_list):
        org_list = []
        org = []
        for w in word_list:
            if w[1]['NamedEntityTag'] in ["GPE", "ORG", "PER"]:
                org.append(w)
            elif org:
                org_list.append(org)
                org = []

        return org_list

    # if query name contains a city, province or country, it should be a headquarter location
    def org_headquarters(self, slot_type):
        def safe_get_sublist(l, target, head_space, tail_space):
            result = []
            target_index = [i for i, x in enumerate(l) if x[0] == target]

            for t in target_index:
                beg = t - head_space
                end = t + tail_space + 1

                if beg >= 0 and end <= len(l):
                    result = l[beg:end]
                elif beg >= 0:
                    result = l[beg:]
                elif beg <= len(l):
                    result = l[:end]
                else:
                    result = [l[t]]
            return result

        gpe_list = []
        if 'country' in slot_type:
            # load country list
            f = io.open('data/dict/country_list', 'r', -1, 'utf-8')
            for line in f:
                gpe_list.append(line.strip())
        elif 'state' in slot_type:
            # load province list
            f = io.open('data/dict/china_province_dict', 'r', -1, 'utf-8')
            for line in f:
                gpe_list.append(line.strip())
        elif 'city' in slot_type:
            # load city list
            china_province_city = cPickle.load(open('data/dict/china_province_city.pkl', 'rb'))
            for p in china_province_city:
                if p['type'] == 0 and p['name'] != (u'台湾' or u'臺灣'):  # type 0 means 直辖市
                    continue
                for c in p['sub']:
                    gpe_list.append(c['name'])
                    if p['name'] == (u'台湾' or u'臺灣'):
                        continue
                    for d in c['sub']:
                        gpe_list.append(d['name'])

        line_outputs = []

        for e in self.evidences[slot_type]:
            query_context = safe_get_sublist(e.parse_result['words'], self.query.name, 1, 0)  # get context word around query

            for w in query_context:
                v = jianfan.ftoj(w[0])
                for element in gpe_list:
                    for r in [u'区', u'县', u'市']:
                        v = v.replace(r, '')

                    if element in w[0] and len(element) > 1:
                        slot_filler = element
                        l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                        # ================ post filtering ================= #
                        if u'友好' in l.slot_filler:
                            continue

                        line_outputs.append(l)

        return line_outputs

