__author__ = 'boliangzhang'

import re

from collections import OrderedDict

class Answer(object):
    def __init__(self, query, run_id='SYS'):
        self.query_id = query.id
        self.output = OrderedDict()
        self.run_id = run_id
        self.query = query
        if query.entity_type == "PER":
            slot_type = PER_SLOT_TYPE
        elif query.entity_type == "ORG":
            slot_type = ORG_SLOT_TYPE
        for s in slot_type:
            self.output[s] = []

    def add_line_output(self, output_line):
        line_output = LineOutput(output_line)
        self.output[line_output.slot_type].append(line_output)

    def generate_html_str(self):
        for slot_type in self.output:
            output = self.output[slot_type]
            for line_output in output:
                try:
                    for w_p in line_output.wide_provenance:
                        replace_d = OrderedDict()

                        if line_output.slot_filler in w_p.text:
                            # highlight slot filler
                            beg = w_p.text.find(line_output.slot_filler)
                            end = beg+len(line_output.slot_filler)+1

                            replace_d[beg] = ('<font style="BACKGROUND-COLOR: #99CCFF">'+line_output.slot_filler+'</font>',
                                              len(line_output.slot_filler))

                        # highlight nearest query name
                        if self.query.name in w_p.text:
                            q_beg = [m.start() for m in re.finditer(self.query.name, w_p.text)]
                            distance = ''
                            for q in q_beg:
                                if q - end > 0:
                                    d = q - end
                                else:
                                    d = beg - q - len(self.query.name)
                                if not distance or d < distance:
                                    nearest_q = q
                                    distance = d

                            replace_d[nearest_q] = ('<font style="BACKGROUND-COLOR: #FF6666">'+self.query.name+'</font>',
                                                    len(self.query.name))

                        # highlight trigger if exist
                        if w_p.trigger:
                            t_beg = [m.start() for m in re.finditer(w_p.trigger, w_p.text)]
                            distance = ''
                            for t in t_beg:
                                if t - end > 0:
                                    d = t - end
                                else:
                                    d = beg - t - len(w_p.trigger)
                                if not distance or d < distance:
                                    nearest_t = t
                                    distance = d

                            replace_d[nearest_t] = ('<font style="BACKGROUND-COLOR: #99FF99">'+w_p.trigger+'</font>',
                                                    len(w_p.trigger))

                        # create html string
                        html_str = ''
                        itr_start = 0
                        for item in sorted(replace_d.items()):
                            beg = item[0]
                            replace_str = item[1][0]
                            length = item[1][1]
                            html_str += w_p.text[itr_start:beg] + replace_str
                            itr_start = beg + length
                        html_str += w_p.text[itr_start:]  # append the last port of string

                        w_p.html_str = html_str
                except:
                    continue

def combine_answer(answer1, answer2):
    if answer1.query_id != answer2.query_id:
        print("answers of different query id can't be combined")
    for s in answer1.output.keys():
        answer1.output[s] += answer2.output[s]
        answer1.output[s] = clean_line_output(answer1.output[s])

    return answer1


class LineOutput(object):
    def __init__(self, output_line=""):
        if output_line == "":
            self.slot_type = ""
            self.wide_provenance = []
            self.slot_filler = ""
            self.slot_filler_prov = []
            self.confidence_score = ""
            self.output_line = ""
        else:
            self.output_line = output_line
            output_line = output_line.strip().split('\t')
            self.slot_type = output_line[1]
            if output_line[3] == "NIL":
                self.wide_provenance = []
                self.slot_filler = ""
                self.slot_filler_prov = []
                self.confidence_score = ""
            else:
                self.wide_provenance = []
                for p in output_line[3].split(','):
                    self.wide_provenance.append(Provenance(string=p))
                self.slot_filler = output_line[4]
                self.slot_filler_prov = []
                for p in output_line[5].split(','):
                    self.slot_filler_prov.append(Provenance(string=p))
                self.confidence_score = output_line[6]

    def __str__(self):
        return self.output_line.encode('utf-8')


class Provenance(object):
    def __init__(self, string=None):
        if string is not None:
            self.doc_id = string.split(':')[0].lower()
            self.beg = int(string.split(':')[1].split('-')[0])
            self.end = int(string.split(':')[1].split('-')[1])
        else:
            self.doc_id = ''
            self.beg = ''
            self.end = ''
            self.inner_beg = ''
            self.inner_end = ''
            self.text = ''
            self.trigger = ''
            self.html_str = ''
            self.inference = False

    def __eq__(self, other):
        return self.doc_id == other.doc_id and self.beg == other.beg and self.end == other.end





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

