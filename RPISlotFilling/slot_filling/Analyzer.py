__author__ = 'boliangzhang'

from Answer import LineOutput
from Answer import Provenance


class Analyzer(object):
    def __init__(self, query, query_evidences, sf_object):
        self.query = query
        self.evidences = query_evidences
        self.sf_object = sf_object
        self.dispatcher = {"per:alternate_names": self.per_alternate_names,
                           "per:date_of_birth": self.per_date_of_birth,
                           "per:age": self.per_age,
                           "per:country_of_birth": self.per_country_of_birth,
                           "per:stateorprovince_of_birth": self.per_stateorprovince_of_birth,
                           "per:city_of_birth": self.per_city_of_birth,
                           "per:origin": self.per_origin,
                           "per:date_of_death": self.per_date_of_death,
                           "per:country_of_death": self.per_country_of_death,
                           "per:stateorprovince_of_death": self.per_stateorprovince_of_death,
                           "per:city_of_death": self.per_city_of_death,
                           "per:cause_of_death": self.per_cause_of_death,
                           "per:countries_of_residence": self.per_countries_of_residence,
                           "per:statesorprovinces_of_residence": self.per_statesorprovinces_of_residence,
                           "per:cities_of_residence": self.per_cities_of_residence,
                           "per:schools_attended": self.per_schools_attended,
                           "per:title": self.per_title,
                           "per:employee_or_member_of": self.per_employee_or_member_of,
                           "per:religion": self.per_religion,
                           "per:spouse": self.per_spouse,
                           "per:children": self.per_children,
                           "per:parents": self.per_parents,
                           "per:siblings": self.per_siblings,
                           "per:other_family": self.per_other_family,
                           "per:charges": self.per_charges,

                           "org:alternate_names": self.org_alternate_names,
                           "org:political_religious_affiliation": self.org_political_religious_affiliation,
                           "org:top_members_employees": self.org_top_members_employees,
                           "org:number_of_employees_members": self.org_number_of_employees_members,
                           "org:members": self.org_members,
                           "org:member_of": self.org_member_of,
                           "org:subsidiaries": self.org_subsidiaries,
                           "org:parents": self.org_parents,
                           "org:founded_by": self.org_founded_by,
                           "org:date_founded": self.org_date_founded,
                           "org:date_dissolved": self.org_date_dissolved,
                           "org:country_of_headquarters": self.org_country_of_headquarters,
                           "org:stateorprovince_of_headquarters": self.org_stateorprovince_of_headquarters,
                           "org:city_of_headquarters": self.org_city_of_headquarters,
                           "org:shareholders": self.org_shareholders,
                           "org:website": self.org_website
                           }

    def create_line_output(self, e, slot_filler, slot_filler_index, slot_type, combined_slot_filler=False, confidence_score=1):
        doc_id = e.doc_id
        parse_result = e.parse_result
        l = LineOutput()
        l.slot_type = slot_type

        evidence_offset_beg = self.sf_object.cleaned_docs[doc_id].find(''.join(parse_result['text']))

        w_p = Provenance()
        w_p.doc_id = doc_id
        cleaned_doc_beg = int(parse_result['words'][0][1]['CharacterOffsetBegin'])
        cleaned_doc_end = int(parse_result['words'][-1][1]['CharacterOffsetEnd'])-1
        if cleaned_doc_beg == 0:
            cleaned_doc_beg += evidence_offset_beg
            cleaned_doc_end += evidence_offset_beg
        w_p.beg = self.sf_object.doc_mapping_table[doc_id][cleaned_doc_beg]
        w_p.end = self.sf_object.doc_mapping_table[doc_id][cleaned_doc_end]
        w_p.text = e.sent_text
        w_p.trigger = e.trigger
        l.wide_provenance = [w_p]

        l.slot_filler = slot_filler

        sf_p = Provenance()
        sf_p.doc_id = doc_id

        if combined_slot_filler:
            cleaned_doc_beg = ''.join(parse_result['text']).find(slot_filler)
            cleaned_doc_end = cleaned_doc_beg+len(slot_filler)-1
        else:
            # here node index in dependency graph need -1 because it start from root which indexed 0
            cleaned_doc_beg = int(parse_result['words'][slot_filler_index-1][1]['CharacterOffsetBegin'])
            cleaned_doc_end = int(parse_result['words'][slot_filler_index-1][1]['CharacterOffsetEnd'])-1
        if int(parse_result['words'][0][1]['CharacterOffsetBegin']) == 0 or combined_slot_filler:
            cleaned_doc_beg += evidence_offset_beg
            cleaned_doc_end += evidence_offset_beg
        sf_p.beg = self.sf_object.doc_mapping_table[doc_id][cleaned_doc_beg]
        sf_p.end = self.sf_object.doc_mapping_table[doc_id][cleaned_doc_end]
        sf_p.text = slot_filler
        l.slot_filler_prov = [sf_p]

        l.confidence_score = confidence_score

        return l

    def get_answer(self, query_answer):
        for slot_type in self.evidences.keys():
            evidences = self.evidences[slot_type]
            if not evidences:
                continue
            try:
                line_outputs = self.dispatcher[slot_type](slot_type)  # list of line_outputs
            except:
                line_outputs = []
            query_answer.output[slot_type] += line_outputs
        return query_answer

    def per_alternate_names(self, slot_type):
        return []

    def per_date_of_birth(self, slot_type):
        return []

    def per_age(self, slot_type):
        return []

    def per_country_of_birth(self, slot_type):
        return []

    def per_stateorprovince_of_birth(self, slot_type):
        return []

    def per_city_of_birth(self, slot_type):
        return []

    def per_origin(self, slot_type):
        return []

    def per_date_of_death(self, slot_type):
        return []

    def per_country_of_death(self, slot_type):
        return []

    def per_stateorprovince_of_death(self, slot_type):
        return []

    def per_city_of_death(self, slot_type):
        return []

    def per_cause_of_death(self, slot_type):
        return []

    def per_countries_of_residence(self, slot_type):
        return []

    def per_statesorprovinces_of_residence(self, slot_type):
        return []

    def per_cities_of_residence(self, slot_type):
        return []

    def per_schools_attended(self, slot_type):
        return []

    def per_title(self, slot_type):
        return []

    def per_employee_or_member_of(self, slot_type):
        return []

    def per_religion(self, slot_type):
        return []

    def per_spouse(self, slot_type):
        return []

    def per_children(self, slot_type):
        return []

    def per_parents(self, slot_type):
        return []

    def per_siblings(self, slot_type):
        return []

    def per_other_family(self, slot_type):
        return []

    def per_charges(self, slot_type):
        return []

    def org_alternate_names(self, slot_type):
        return []

    def org_political_religious_affiliation(self, slot_type):
        return []

    def org_top_members_employees(self, slot_type):
        return []

    def org_number_of_employees_members(self, slot_type):
        return []

    def org_members(self, slot_type):
        return []

    def org_member_of(self, slot_type):
        return []

    def org_subsidiaries(self, slot_type):
        return []

    def org_parents(self, slot_type):
        return []

    def org_founded_by(self, slot_type):
        return []

    def org_date_founded(self, slot_type):
        return []

    def org_date_dissolved(self, slot_type):
        return []

    def org_country_of_headquarters(self, slot_type):
        return []

    def org_stateorprovince_of_headquarters(self, slot_type):
        return []

    def org_city_of_headquarters(self, slot_type):
        return []

    def org_shareholders(self, slot_type):
        return []

    def org_website(self, slot_type):
        return []




