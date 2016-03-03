#encoding=utf-8
__author__ = 'boliangzhang'

import io
import itertools
import re
import jianfan
import cPickle
import datetime
import copy

from RPISlotFilling.dependency_tree.DependencyTree import DependenceTree

from Analyzer import Analyzer


class DependencyAnalyzer(Analyzer):
    def __init__(self, query, query_evidences, sf_object):
        Analyzer.__init__(self, query, query_evidences, sf_object)

    def per_alternate_names(self, slot_type):
        line_outputs = []
        for e in self.evidences[slot_type]:
            trigger = e.trigger
            if trigger == '':
                continue

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 3:
                        continue

                    k_step_node = dpt.k_step_node(t, 2)
                    for node in k_step_node:
                        if node.value == self.query.name:
                            continue
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'PERSON':
                            l = self.create_line_output(e, node.value, node.index, slot_type)

                            # ================ post filtering ================= #
                            if len(l.slot_filler) < 2:
                                continue
                            if l.slot_filler in [u'中国道教协会']:
                                continue

                            line_outputs.append(l)

        return line_outputs

    def per_date_of_birth(self, slot_type):
        line_outputs = self.date(slot_type)
        return line_outputs

    def per_age(self, slot_type):
        line_outputs = []
        for e in self.evidences[slot_type]:
            trigger_word = e.trigger
            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 4:
                        continue

                    k_step_node = dpt.k_step_node(t, 2)

                    age_kw = [u'岁', u'歲']  # key words help to find age number
                    for node in k_step_node:
                        if node.value not in age_kw:
                            continue
                        # find integer near age key word within 2 steps
                        k_step_node = dpt.k_step_node(node, 2)

                        for n in k_step_node:
                            if self.is_number(n.value):
                                l = self.create_line_output(e, n.value, n.index, slot_type)

                                line_outputs.append(l)

            return line_outputs

    def per_country_of_birth(self, slot_type):
        line_outputs = self.country(slot_type)
        return line_outputs

    def per_stateorprovince_of_birth(self, slot_type):
        line_outputs = self.stateorprovince(slot_type)
        return line_outputs

    def per_city_of_birth(self, slot_type):
        line_outputs = self.city(slot_type)
        return line_outputs

    def per_origin(self, slot_type):
        line_outputs = self.country(slot_type)
        return line_outputs

    def per_date_of_death(self, slot_type):
        line_outputs = self.date(slot_type)
        return line_outputs

    def per_country_of_death(self, slot_type):
        line_outputs = self.country(slot_type)
        return line_outputs

    def per_stateorprovince_of_death(self, slot_type):
        line_outputs = self.stateorprovince(slot_type)
        return line_outputs

    def per_city_of_death(self, slot_type):
        line_outputs = self.city(slot_type)
        return line_outputs

    def per_cause_of_death(self, slot_type):
        per_cause_of_death_line_outputs = []
        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 4:
                        continue

                    l = self.create_line_output(e, t.value, t.index, slot_type)

                    per_cause_of_death_line_outputs.append(l)

        return per_cause_of_death_line_outputs

    def per_countries_of_residence(self, slot_type):
        line_outputs = self.country(slot_type)
        return line_outputs

    def per_statesorprovinces_of_residence(self, slot_type):
        line_outputs = self.stateorprovince(slot_type)
        return line_outputs

    def per_cities_of_residence(self, slot_type):
        line_outputs = self.city(slot_type)
        return line_outputs

    def per_schools_attended(self, slot_type):
        # load chinese school dict
        chinese_school = dict()
        f = io.open('data/dict/school_list', 'r', -1, 'utf-8').read()
        f = f.split('\n\n')
        for schools in f:
            province = schools.strip().split('\n')[0]
            chinese_school[province] = schools.split('\n')[1:]

        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 3:
                        continue

                    # ========================== school name string match ======================= #
                    if t.index - 2 < 0:
                        text_around_trigger = ''.join(e.parse_result['text'][: t.index + 3])
                    elif t.index + 2 > len(e.parse_result['text']) - 1:
                        text_around_trigger = ''.join(e.parse_result['text'][t.index - 3:])
                    else:
                        text_around_trigger = ''.join(e.parse_result['text'][t.index - 3: t.index + 3])

                    schools = list(itertools.chain(*chinese_school.values()))
                    for s in schools:
                        s_cleaned = re.sub(r'\([^)]*\)', '', s)
                        if s_cleaned in text_around_trigger:
                            l = self.create_line_output(e, s_cleaned, 0, slot_type, combined_slot_filler=True)

                            line_outputs.append(l)

                    # ========================== pattern match ======================= #

                    # school_near_trigger = dpt.k_step_node(t, 2)
                    #
                    # for s in school_near_trigger:
                    #     if s.value[-1] in [u'学', u'中', u'校', u'社', u'院']:
                    #         # given a sequence, last element contains 学, 中 or 校, recursively inverse scan until
                    #         # find GPE or ORG, ajacent GPE or ORG will be both considered part of school name
                    #         def find_school(l):
                    #             word = []
                    #             if l[-1][1]['NamedEntityTag'] != ('GPE' or 'ORG'):
                    #                 word.append(l[-1])
                    #                 if len(l) > 1:
                    #                     word += find_school(l[:-1])
                    #                 return word
                    #             elif l[-1][1]['NamedEntityTag'] == ('GPE' or 'ORG'):
                    #                 if len(l) == 1:
                    #                     return [l[-1]]
                    #                 elif l[-2][1]['NamedEntityTag'] != ('GPE' or 'ORG'):
                    #                     return [l[-1]]
                    #                 else:
                    #                     word.append(l[-1])
                    #                     if len(l) > 1:
                    #                         word += find_school(l[:-1])
                    #                     return word
                    #
                    #             return word
                    #
                    #         index = s.index - 1
                    #         if index - 5 > 0:
                    #             words = find_school(e.parse_result['words'][index-5:index+1])
                    #         else:
                    #             words = find_school(e.parse_result['words'][:index])
                    #
                    #         if len(words) < 5 and words[-1][1]['NamedEntityTag'] == ('GPE' or 'ORG'):
                    #             doc_id = '_'.join(e[0].split('_')[:-1])
                    #             sentence_id = e[0]
                    #
                    #             l = LineOutput()
                    #             l.slot_type = 'per:schools_attended'
                    #             l.run_id = 'SYS'
                    #
                    #             p = Provenance()
                    #             p.doc_id = doc_id
                    #             p.sentence_id = sentence_id
                    #             query_seg_doc_beg = int(e.parse_result['words'][0][1]['CharacterOffsetBegin'])
                    #             query_seg_doc_end = int(e.parse_result['words'][-1][1]['CharacterOffsetEnd'])-1
                    #             p.beg = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_beg]
                    #             p.end = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_end]
                    #             l.wide_provenance = [p]
                    #
                    #             l.slot_filler = ''.join(reversed([w[0] for w in words]))
                    #
                    #             p = Provenance()
                    #             p.doc_id = doc_id
                    #             p.sentence_id = sentence_id
                    #             query_seg_doc_beg = int(words[-1][1]['CharacterOffsetBegin'])
                    #             query_seg_doc_end = int(words[0][1]['CharacterOffsetEnd']) - 1
                    #             p.beg = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_beg]
                    #             p.end = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_end]
                    #             l.slot_filler_prov = [p]
                    #
                    #             l.confidence_score = 1
                    #
                    #             line_outputs.append(l)

        return line_outputs

    def per_title(self, slot_type):
        line_outputs = []
        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            # here trigger node is title
            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    if len(min(paths, key=len)) > 3:
                        continue

                    if jianfan.ftoj(t.value) == u'记者':
                        continue

                    l = self.create_line_output(e, t.value, t.index, slot_type)

                    # ================ post filtering ================= #
                    # if there is a per in between a query and a title, the title is incorrect
                    path_node_type = []
                    query_word_index = q.index - 1
                    trigger_word_index = t.index - 1
                    for word in e.parse_result['words'][query_word_index+1:trigger_word_index]:
                        path_node_type.append(word[1]['NamedEntityTag'])
                    for word in e.parse_result['words'][trigger_word_index+1:query_word_index]:
                        path_node_type.append(word[1]['NamedEntityTag'])
                    if 'PERSON' in path_node_type:
                        continue

                    if len(l.slot_filler) < 2:
                        continue

                    line_outputs.append(l)

        return line_outputs

    def per_employee_or_member_of(self, slot_type):
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
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    if len(min(paths, key=len)) > 3:
                        continue

                    org_near_t = dpt.k_step_node(t, 2)

                    def find_org_after_t(l):
                        org = []
                        if l != [] and l[0][1]['NamedEntityTag'] == 'ORG':
                            org.append(l[0])
                            if len(l) > 1:
                                org += find_org_after_t(l[1:])
                        return org

                    def find_org_before_t(l):
                        org = []
                        if l != [] and l[-1][1]['NamedEntityTag'] == 'ORG':
                            org.append(l[-1])
                            if len(l) > 1:
                                org += find_org_before_t(l[:-1])
                        return org

                    for org in org_near_t:
                        org_word_index = org.index - 1
                        org_before_t = []
                        org_after_t = []
                        for i in xrange(len(e.parse_result['words'][org_word_index+1:])):
                            if e.parse_result['words'][org_word_index+1+i][1]['NamedEntityTag'] == 'ORG':
                                org_after_t = find_org_after_t(e.parse_result['words'][org_word_index+i+1:])
                                break
                        for i in xrange(len(e.parse_result['words'][:org_word_index])):
                            if e.parse_result['words'][org_word_index-i-1][1]['NamedEntityTag'] == 'ORG':
                                org_before_t = find_org_before_t(e.parse_result['words'][:org_word_index-i])
                                break

                        if org_after_t == [] and org_before_t == []:
                            continue

                        org_before_t = org_before_t[::-1]  # reverse list
                        answer = []

                        if org_after_t != [] and org_before_t != []:
                            if e.parse_result['words'][org_word_index][1]['NamedEntityTag'] == 'ORG':
                                if org_word_index == e.parse_result['words'].index(org_before_t[-1]) + 1 and \
                                                        org_word_index == e.parse_result['words'].index(org_after_t[0]) - 1:
                                    answer = org_before_t + [e.parse_result['words'][org_word_index]] + org_after_t
                                elif org_word_index == e.parse_result['words'].index(org_before_t[-1]) + 1:
                                    answer = org_before_t + [e.parse_result['words'][org_word_index]]
                                elif org_word_index == e.parse_result['words'].index(org_after_t[0]) - 1:
                                    answer = [e.parse_result['words'][org_word_index]] + org_after_t
                            elif org_word_index - e.parse_result['words'].index(org_before_t[-1]) < 3:
                                answer = org_before_t
                            elif e.parse_result['words'].index(org_after_t[0]) - org_word_index < 3:
                                answer = org_after_t

                        elif org_before_t != []:
                            if e.parse_result['words'][org_word_index][1]['NamedEntityTag'] == 'ORG' and \
                                                    org_word_index == e.parse_result['words'].index(org_before_t[-1]) + 1:
                                    answer += org_before_t + [e.parse_result['words'][org_word_index]]
                            elif org_word_index - e.parse_result['words'].index(org_before_t[-1]) < 3:
                                answer = org_before_t

                        elif org_after_t != []:
                            if e.parse_result['words'][org_word_index][1]['NamedEntityTag'] == 'ORG' and \
                                                    org_word_index == e.parse_result['words'].index(org_after_t[0]) - 1:
                                    answer += [e.parse_result['words'][org_word_index]] + org_after_t
                            elif e.parse_result['words'].index(org_after_t[0]) - org_word_index < 3:
                                answer = org_after_t

                        if answer == []:
                            continue

                        if (u'新华社' or u'中央社') in jianfan.ftoj(''.join([w[0] for w in answer])):
                            continue

                        slot_filler = ''.join([w[0] for w in answer])
                        l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                        # ================ post filtering ================= #
                        incorrect_slot_filler = False
                        # remove org in quote mark or book title mark
                        marks = [(u'"', u'"'), (u'《', u'》'), (u'【', u'】'), (u'<', u'>'), (u'[', u']'), (u"'", u"'")]
                        for element in marks:
                            substring = iter_find_sublist(element[0], element[1], e.parse_result['text'])
                            for s in substring:
                                if l.slot_filler in ''.join(e.parse_result['text'][s[0]: s[1]]):
                                    incorrect_slot_filler = True
                                    break

                        # if there is a '、' between a query and an answer, the answer should be ignored
                        query_node_index = q.index - 1
                        org_end_node_index = e.parse_result['words'].index(answer[-1])
                        if u'、' in ''.join(e.parse_result['text'][query_node_index:org_end_node_index]):
                            incorrect_slot_filler = True
                        if u'、' in ''.join(e.parse_result['text'][org_end_node_index:query_node_index]):
                            incorrect_slot_filler = True

                        if incorrect_slot_filler is True:
                            continue

                        line_outputs.append(l)

        return line_outputs

    def per_religion(self, slot_type):
        line_outputs = []
        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    if len(min(paths, key=len)) > 5:
                        continue

                    l = self.create_line_output(e, t.value, t.index, slot_type)

                    line_outputs.append(l)
        return line_outputs

    def per_children(self, slot_type):
        line_outputs = self.parent_child(slot_type)
        return line_outputs

    def per_parents(self, slot_type):
        line_outputs = self.parent_child(slot_type)
        return line_outputs

    def per_siblings(self, slot_type):
        line_outputs = self.parent_child(slot_type)
        return line_outputs

    def per_other_family(self, slot_type):
        line_outputs = self.parent_child(slot_type)
        return line_outputs

    ########################## organization #########################
    def org_top_members_employees(self, slot_type):
        line_outputs = []
        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    if len(min(paths, key=len)) > 3:
                        continue

                    if jianfan.ftoj(t.value) == u'记者':
                        continue

                    k_step_node = dpt.k_step_node(t, 2)
                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'PERSON':
                            l = self.create_line_output(e, node.value, node.index, slot_type)

                            # ================ post filtering ================= #
                            # if there is a '、' between a query and an answer, the answer should be ignored
                            query_node_index = q.index - 1
                            answer_index = node.index - 1
                            if u'、' in ''.join(e.parse_result['text'][query_node_index:answer_index]):
                                continue
                            if u'、' in ''.join(e.parse_result['text'][answer_index:query_node_index]):
                                continue

                            # if there is a ORG in between a query and a person, the person is unlikely to be a top member
                            path_node_type = []
                            query_word_index = q.index - 1
                            trigger_word_index = node.index - 1
                            for word in e.parse_result['words'][query_word_index+1:trigger_word_index]:
                                path_node_type.append(word[1]['NamedEntityTag'])
                            for word in e.parse_result['words'][trigger_word_index+1:query_word_index]:
                                path_node_type.append(word[1]['NamedEntityTag'])
                            if 'ORG' in path_node_type:
                                continue

                            if l.slot_filler in [u'少林寺']:
                                continue

                            line_outputs.append(l)

        return line_outputs

    def org_number_of_employees_members(self, slot_type):
        # line_outputs = []
        # for e in self.evidences[slot_type:
        #     trigger_word = e.trigger
        #
        #     dpt = Dependence.parse_resulte(e.parse_result['dependencies'])
        #
        #     query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)
        #
        #     for q in query_node:
        #         for t in trigger_node:
        #             paths = dpt.find_undirected_path(q, t)
        #             if not paths:
        #                 continue
        #             if len(min(paths, key=len)) > 4:
        #                 continue
        #
        #             # if node adjacent to trigger node has number in string, it's the answer
        #             k_step_node = dpt.k_step_node(t, 1)
        #             for node in k_step_node:
        #                 try:
        #                     # convert chinese number to arabic number
        #                     number = getResultForDigit(node.value)
        #                     break
        #                 except:
        #                     try:
        #                         number = int(re.search(r'\d+', node.value).group())  # extract number from string
        #                         break
        #                     except:
        #                         number = -1
        #
        #             # if node near trigger node is a number, it's the answer
        #             if number == -1:
        #                 k_step_node = dpt.k_step_node(t, 2)
        #                 for node in k_step_node:
        #                     # if node value can be converted to number, it's the slot filler
        #                     try:
        #                         number = int(node.value)  # extract number from string
        #                         break
        #                     except:
        #                         # convert chinese number to arabic number
        #                         try:
        #                             number = getResultForDigit(node.value)
        #                             break
        #                         except:
        #                             number = -1
        #
        #             if number == -1:
        #                 continue
        #
        #             doc_id = '_'.join(e[0].split('_')[:-1])
        #             sentence_id = e[0]
        #
        #             l = LineOutput()
        #             l.slot_type = 'org:number_of_employees_members'
        #             l.run_id = 'SYS'
        #
        #             p = Provenance()
        #             p.doc_id = doc_id
        #             p.sentence_id = sentence_id
        #             query_seg_doc_beg = int(e.parse_result['words'][0][1]['CharacterOffsetBegin'])
        #             query_seg_doc_end = int(e.parse_result['words'][-1][1]['CharacterOffsetEnd'])-1
        #             p.beg = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_beg]
        #             p.end = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_end]
        #             l.wide_provenance = [p]
        #
        #             l.slot_filler = str(number)
        #
        #             p = Provenance()
        #             p.doc_id = doc_id
        #             p.sentence_id = sentence_id
        #             query_seg_doc_beg = int(e.parse_result['words'][node.index-1][1]['CharacterOffsetBegin'])
        #             query_seg_doc_end = int(e.parse_result['words'][node.index-1][1]['CharacterOffsetEnd'])-1
        #             p.beg = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_beg]
        #             p.end = cleaned_doc_offset_mapping[query][doc_id][query_seg_doc_end]
        #             l.slot_filler_prov = [p]
        #
        #             l.confidence_score = 1
        #
        #             line_outputs.append(l)
        #
        #
        # if len(line_outputs) > 0:
        #     return line_outputs
        # else:
        #     l = LineOutput()
        #     l.run_id = 'SYS'
        #     return [l]
        return []

    def org_members(self, slot_type):
        # line_outputs = []
        # for e in self.evidences[slot_type:
        #     trigger_word = e.trigger
        #
        #     dpt = Dependence.parse_resulte(e.parse_result['dependencies'])
        #
        #     query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)
        #
        #     for q in query_node:
        #         for t in trigger_node:
        #             paths = dpt.find_undirected_path(q, t)
        #             if not paths:
        #                 continue
        #             if len(min(paths, key=len)) > 3:
        #                 continue
        #
        #             k_step_node = dpt.k_step_node(t, 2)
        #             for node in k_step_node:
        #                 if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'PERSON':
        #                     l = create_line_output(e, node, query, 'org:members')
        #
        #                     # ================ post filtering ================= #
        #                     # if there is a '、' between a query and an answer, the answer should be ignored
        #                     query_node_index = q.index - 1
        #                     answer_index = node.index - 1
        #                     if u'、' in ''.join(e.parse_result['text'][query_node_index:answer_index]):
        #                         continue
        #                     if u'、' in ''.join(e.parse_result['text'][answer_index:query_node_index]):
        #                         continue
        #
        #                     line_outputs.append(l)
        #
        #
        # if len(line_outputs) > 0:
        #     return line_outputs
        # else:
        #     l = LineOutput()
        #     l.run_id = 'SYS'
        #     return [l]
        return []

    def org_member_of(self, slot_type):
        # line_outputs = []
        # for e in self.evidences[slot_type:
        #     trigger_word = e.trigger
        #
        #     dpt = Dependence.parse_resulte(e.parse_result['dependencies'])
        #
        #     query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)
        #
        #     for q in query_node:
        #         for t in trigger_node:
        #             paths = dpt.find_undirected_path(q, t)
        #             if not paths:
        #                 continue
        #             if len(min(paths, key=len)) > 3:
        #                 continue
        #
        #             k_step_node = dpt.k_step_node(t, 2)
        #             for node in k_step_node:
        #                 if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'ORG' and node.value != self.query.name:
        #                     l = create_line_output(e, node, query, 'org:member_of')
        #                     line_outputs.append(l)
        #
        #
        # if len(line_outputs) > 0:
        #     return line_outputs
        # else:
        #     l = LineOutput()
        #     l.run_id = 'SYS'
        #     return [l]
        return []

    def org_founded_by(self, slot_type):
        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger_word = e.trigger
            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 4:
                        continue

                    k = 2
                    k_step_node = dpt.k_step_node(t, k)

                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] != 'PERSON' or \
                                        node.value in self.query.name or self.query.name in node.value:
                            continue
                        # if node.upper_dependency == 'prep':
                        # ajacent_node = dpt.k_step_node(node, 1)
                        # for n in ajacent_node:
                        # convert traditional chinese to simplified chinese, fuzzy match by longest common string
                        # if len(long_substr([n.value, c])) > 1:
                        if node.index > t.index:
                                l = self.create_line_output(e, node.value, node.index, slot_type)

                                line_outputs.append(l)

        return line_outputs

    def org_date_founded(self, slot_type):
        line_outputs = self.date(slot_type)
        return line_outputs

    def org_date_dissolved(self, slot_type):
        line_outputs = self.date(slot_type)
        return line_outputs

    def org_country_of_headquarters(self, slot_type):
        line_outputs = self.country(slot_type)
        return line_outputs

    def org_stateorprovince_of_headquarters(self, slot_type):
        line_outputs = self.stateorprovince(slot_type)
        return line_outputs

    def org_city_of_headquarters(self, slot_type):
        line_outputs = self.city(slot_type)
        return line_outputs

    def org_shareholders(self, slot_type):
        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger_word = e.trigger

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            org_list = self.find_org(e.parse_result['words'])

            shareholders = []
            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    for org in org_list:
                        min_distance = 100
                        for node in org:
                            path = dpt.find_undirected_path(t, node)
                            if not path:
                                continue
                            shortest_path = min(paths, key=len)
                            if len(shortest_path) - 1 < min_distance:
                                min_distance = len(shortest_path)
                        if min_distance < 4:
                            shareholders.append(org)

            for org in shareholders:
                slot_filler = ''.join([w[0] for w in org])
                l = self.create_line_output(e, slot_filler, 0, slot_type, combined_slot_filler=True)

                line_outputs.append(l)

        return line_outputs

    ########################## utilities #########################
    # find longest common substring, input is a list of strings
    def long_substr(self, data):
        def is_substr(find, data):
            if len(data) < 1 and len(find) < 1:
                return False
            for i in range(len(data)):
                if find not in data[i]:
                    return False
            return True

        substr = ''
        if len(data) > 1 and len(data[0]) > 0:
            for i in range(len(data[0])):
                for j in range(len(data[0])-i+1):
                    if j > len(substr) and is_substr(data[0][i:i+j], data):
                        substr = data[0][i:i+j]
        return substr

    # same as find_org in PatternAnalyzer
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

    def is_number(self, s):
            try:
                float(s)
                return True
            except ValueError:
                return False

    def find_query_trigger_node(self, query_name, dpt, trigger_word):
        query_node = []
        trigger_node = []

        query_node += dpt.find_node(query_name)
        query_node += dpt.find_node(jianfan.jtof(query_name))
        trigger_node += dpt.find_node(trigger_word)
        trigger_node += dpt.find_node(jianfan.jtof(trigger_word))

        return query_node, trigger_node

    def date(self, slot_type):
        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger_word = e.trigger
            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:

                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 3:
                        continue

                    k = 2
                    k_step_node = dpt.k_step_node(t, k)
                    year = []
                    y_node = []
                    month = 'XX'
                    m_node = None
                    day = 'XX'
                    d_node = None
                    for node in k_step_node:
                        if u'年' in node.value:
                            try:
                                year.append(int(re.search(r'\d+', node.value).group()))
                            except:
                                continue
                            y_node.append(node)
                            node_around_year = dpt.k_step_node(node, 2)
                            for n in node_around_year:
                                if u'月' in n.value:
                                    try:
                                        month = int(re.search(r'\d+', n.value).group())
                                        m_node = n
                                    except:
                                        pass

                                if u'日' in n.value:
                                    try:
                                        day = int(re.search(r'\d+', n.value).group())
                                        d_node = n
                                    except:
                                        pass

                        elif (u'时' or u'分') in jianfan.ftoj(node.value):
                            node_around = dpt.k_step_node(node, 1)
                            for n_around in node_around:
                                if u'年' in node.value:
                                    try:
                                        year.append(int(re.search(r'\d+', n_around.value).group()))
                                    except:
                                        continue
                                    y_node.append(n_around)
                                    node_around_year = dpt.k_step_node(n_around, 2)
                                    for n in node_around_year:
                                        if u'月' in n.value:
                                            try:
                                                month = int(re.search(r'\d+', n.value).group())
                                                m_node = n
                                            except:
                                                pass

                                        if u'日' in n.value:
                                            try:
                                                day = int(re.search(r'\d+', n.value).group())
                                                d_node = n
                                            except:
                                                pass

                        if len(year) == 0:
                            continue

                        if 'death' in slot_type or 'dissolved' in slot_type:
                            final_year = max(year)
                            if final_year < 1900:
                                continue
                            final_y_node = y_node[year.index(final_year)]
                        if 'birth' in slot_type or 'founded' in slot_type:
                            tmp_year = []
                            for y in year:  # year less than 1900 is invalid
                                if y > 1900:
                                    tmp_year.append(y)
                            if not tmp_year:
                                continue

                            final_year = min(tmp_year)
                            final_y_node = y_node[year.index(final_year)]

                        # create line output
                        # decide slot filler
                        if month == 'XX' and day == 'XX':
                            dt = datetime.datetime(final_year, 1, 1)
                            slot_filler = dt.strftime("%Y-%m-%d").split('-')[0] + '-XX-XX'
                        elif day == 'XX':
                            dt = datetime.datetime(final_year, month, 1)
                            slot_filler = '-'.join(dt.strftime("%Y-%m-%d").split('-')[:2]) + '-XX'
                        elif month == 'XX':
                            dt = datetime.datetime(final_year, 1, 1)
                            slot_filler = dt.strftime("%Y-%m-%d").split('-')[0] + '-XX-XX'
                        else:
                            dt = datetime.datetime(final_year, month, day)
                            slot_filler = dt.strftime("%Y-%m-%d")

                        # decide slot filler index
                        if d_node is not None:
                            slot_filler_index = d_node.index
                        elif m_node is not None:
                            slot_filler_index = m_node.index
                        else:
                            slot_filler_index = final_y_node.index

                        # compute confidence score
                        paths = dpt.find_undirected_path(node, t)
                        if not paths:
                            confidence_score = 1
                        else:
                            confidence_score = 1 - len(min(paths, key=len)) / k

                        l = self.create_line_output(e, slot_filler, slot_filler_index,
                                                    slot_type, confidence_score=confidence_score)

                        line_outputs.append(l)

        return line_outputs

    def country(self, slot_type):
        line_outputs = []

        # load country list
        country_list = []
        f = io.open('data/dict/country_list', 'r', -1, 'utf-8')
        for line in f:
            country_list.append(line.strip())

        for e in self.evidences[slot_type]:
            evidence_used = False
            trigger_word = e.trigger

            # some org evidences only have query name but no trigger word, they are used for pattern matching
            if trigger_word == self.query.name:
                continue

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 3:
                        continue

                    # set different k for org and per
                    if 'org' in slot_type:
                        k = 2
                    elif 'per' in slot_type:
                        k = 3
                    k_step_node = dpt.k_step_node(t, k)

                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'O':
                            continue
                        for c in country_list:
                            if c in node.value and len(node.value.replace(c, '')) < 2:
                                l = self.create_line_output(e, node.value, node.index, slot_type)

                                line_outputs.append(l)

                                evidence_used = True
                                break

                    if evidence_used is True:
                        break

        return line_outputs

    def stateorprovince(self, slot_type):
        line_outputs = []

        # load china province list
        province_dict = []
        f = io.open('data/dict/china_province_dict', 'r', -1, 'utf-8')
        for line in f:
            province_dict.append(line.strip())

        for e in self.evidences[slot_type]:
            evidence_used = False
            trigger_word = e.trigger

            # some org evidences only have query name but no trigger word, they are used for pattern matching
            if trigger_word == self.query.name:
                continue

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:

                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue
                    if len(min(paths, key=len)) > 4:
                        continue

                    # set different k for org and per
                    if 'org' in slot_type:
                        k = 2
                    elif 'per' in slot_type:
                        k = 2
                    k_step_node = dpt.k_step_node(t, k)

                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'O':
                            continue
                        value = jianfan.ftoj(node.value).replace(u'省', '')
                        for province in province_dict:
                            # if province == value and len(value.replace(province, '')) < 2:
                            if province == value:
                                l = self.create_line_output(e, node.value, node.index, slot_type)

                                # compute confidence score
                                paths = dpt.find_undirected_path(node, t)
                                if not paths:
                                    l.confidence_score = 1
                                else:
                                    l.confidence_score = 1 - len(min(paths, key=len)) / k

                                # ================ post filtering ================= #
                                if u'友好' in l.slot_filler:
                                    continue

                                line_outputs.append(l)

                                evidence_used = True
                                break

                    if evidence_used is True:
                        break

        return line_outputs

    def city(self, slot_type):
        line_outputs = []

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

        for e in self.evidences[slot_type]:
            evidence_used = False
            trigger_word = e.trigger

            # some org evidences only have query name but no trigger word, they are used for pattern matching
            if trigger_word == self.query.name:
                continue

            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 4:
                        continue

                    # set different k for org and per
                    if 'org' in slot_type:
                        k = 2
                    elif 'per' in slot_type:
                        k = 3
                    k_step_node = dpt.k_step_node(t, k)

                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] == 'O':
                            continue
                        # if node.upper_dependency == 'prep':
                        # ajacent_node = dpt.k_step_node(node, 1)
                        # for n in ajacent_node:
                        # convert traditional chinese to simplified chinese, fuzzy match by longest common string
                        # if len(long_substr([n.value, c])) > 1:
                        v = jianfan.ftoj(copy.deepcopy(node.value))
                        for c in city_list:
                            for r in [u'区', u'县', u'市']:
                                v = v.replace(r, '')

                            if v == c and len(node.value) > 1:
                                l = self.create_line_output(e, node.value, node.index, slot_type)

                                # compute confidence score
                                paths = dpt.find_undirected_path(node, t)
                                if not paths:
                                    l.confidence_score = 1
                                else:
                                    l.confidence_score = 1 - len(min(paths, key=len)) / k

                                # ================ post filtering ================= #
                                if u'友好' in l.slot_filler:
                                    continue

                                line_outputs.append(l)

                                evidence_used = True
                                break

                    if evidence_used is True:
                        break

        return line_outputs

    def parent_child(self, slot_type):
        line_outputs = []

        for e in self.evidences[slot_type]:
            trigger_word = e.trigger
            dpt = DependenceTree(e.parse_result['dependencies'])

            query_node, trigger_node = self.find_query_trigger_node(self.query.name, dpt, trigger_word)

            for q in query_node:
                for t in trigger_node:
                    paths = dpt.find_undirected_path(q, t)
                    if not paths:
                        continue

                    if len(min(paths, key=len)) > 4:
                        continue

                    k_step_node = dpt.k_step_node(t, 3)

                    for node in k_step_node:
                        if e.parse_result['words'][node.index-1][1]['NamedEntityTag'] != 'PERSON' or \
                                        node.value in self.query.name or self.query.name in node.value:
                            continue
                        # if node.upper_dependency == 'prep':
                        # ajacent_node = dpt.k_step_node(node, 1)
                        # for n in ajacent_node:
                        # convert traditional chinese to simplified chinese, fuzzy match by longest common string
                        # if len(long_substr([n.value, c])) > 1:
                        if node.index > t.index:
                                l = self.create_line_output(e, node.value, node.index, slot_type)

                                line_outputs.append(l)

        return line_outputs
