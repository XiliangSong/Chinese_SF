import io
import os
from collections import OrderedDict


def evaluate_runs(tab_path):
    assessment_path = \
        '../../data/LDC/LDC2015E67_TAC_KBP_2014_Chinese_Regular_Slot_Filling_Evaluation_Assessment_Results_V2.0/data/'

    # load tab file
    tab = [line.split('\t') for line in io.open(tab_path, 'r', -1, 'utf-8').read().splitlines()]

    # load assessment
    assessments = []
    for file_name in os.listdir(assessment_path):
        if 'SF14' not in file_name:
            continue

        assessments += [line.split('\t') for line in
                        io.open(os.path.join(assessment_path, file_name), 'r', -1, 'utf-8').read().strip().splitlines()]

    slots = ['per:age', 'per:alternate_names', 'per:cause_of_death', 'per:charges', 'per:children',
             'per:cities_of_residence', 'per:city_of_birth', 'per:city_of_death', 'per:countries_of_residence',
             'per:country_of_birth', 'per:country_of_death', 'per:date_of_birth', 'per:date_of_death',
             'per:employee_or_member_of', 'per:origin', 'per:other_family', 'per:parents', 'per:religion',
             'per:schools_attended', 'per:siblings', 'per:spouse', 'per:stateorprovince_of_birth',
             'per:stateorprovince_of_death', 'per:statesorprovinces_of_residence', 'per:title', 'org:alternate_names',
             'org:city_of_headquarters', 'org:country_of_headquarters', 'org:date_dissolved', 'org:date_founded',
             'org:founded_by', 'org:member_of', 'org:members', 'org:number_of_employees_members', 'org:parents',
             'org:political_religious_affiliation', 'org:shareholders', 'org:stateorprovince_of_headquarters',
             'org:subsidiaries', 'org:top_members_employees', 'org:website']

    stats = OrderedDict()
    for s in slots:
        for item in assessments:
            if s in item[1]:
                try:
                    stats[s] += 1
                except KeyError:
                    stats[s] = 1

        if s not in stats:
            stats[s] = 0

    assessment_corrected_entries = 0
    assessment_corrected_entries_by_type = OrderedDict()
    for slot_type in slots:
        assessment_corrected_entries_by_type[slot_type] = 0
    for item in assessments:
        if item[7] == '1':
            assessment_corrected_entries += 1
            slot_type = ':'.join(item[1].split(':')[1:])
            assessment_corrected_entries_by_type[slot_type] += 1

    assert sum(stats.values()) == len(assessments)

    print '--> LDC assessment response stats:'
    print '\tentries: %s' % str(len(assessments))
    print '\n'.join(['\t'+'\t'.join((item[0], str(item[1]))) for item in stats.items()])

    evaluated_entry_num = 0
    slot_filler_correct_entry_num = 0
    provenance_correct_entry_num = 0
    overall_correct_entry_num = 0

    evaluated_entry_num_by_type = OrderedDict()
    for slot_type in slots:
        evaluated_entry_num_by_type[slot_type] = 0
    slot_filler_correct_entry_by_type = OrderedDict()
    for slot_type in slots:
        slot_filler_correct_entry_by_type[slot_type] = 0
    provenance_correct_entry_by_type = OrderedDict()
    for slot_type in slots:
        provenance_correct_entry_by_type[slot_type] = 0
    overall_correct_entry_by_type = OrderedDict()
    for slot_type in slots:
        overall_correct_entry_by_type[slot_type] = 0

    for entry in tab:
        for item in assessments:
            if entry[3] == 'NIL':
                continue
            if entry[4] == item[3] and entry[5] == item[4] and entry[3] == item[2]:
                slot_type = ':'.join(item[1].split(':')[1:])
                evaluated_entry_num_by_type[slot_type] += 1

                evaluated_entry_num += 1
                if item[5] in ['C', 'R']:
                    slot_filler_correct_entry_num += 1
                    slot_filler_correct_entry_by_type[slot_type] += 1

                if item[6] in ['C']:
                    provenance_correct_entry_num += 1
                    provenance_correct_entry_by_type[slot_type] += 1

                if item[7] == '1':
                    overall_correct_entry_num += 1
                    overall_correct_entry_by_type[slot_type] += 1

    print '\n-->evaluated tab file:'

    print '\tgold entries: %s' % str(assessment_corrected_entries)

    print '\tevaluated entries: %s' % str(evaluated_entry_num)

    slot_filler_precision = 1.0*slot_filler_correct_entry_num/evaluated_entry_num
    print '\tcorrect slot filler entries: %s, precision: %s' % (str(slot_filler_correct_entry_num),
                                                      str(round(slot_filler_precision, 2)))
    provenance_precision = 1.0*provenance_correct_entry_num/evaluated_entry_num
    print '\tcorrect provenance entries %s, precision: %s' % (str(provenance_correct_entry_num),
                                                                str(round(provenance_precision, 2)))
    overall_precision = 1.0*overall_correct_entry_num/evaluated_entry_num
    print '\toverall correct: %s, precision: %s' % (str(overall_correct_entry_num),
                                                  str(round(overall_precision, 2)))
    overall_recall = 1.0*overall_correct_entry_num/assessment_corrected_entries
    print '\toverall recall: %s' % str(round(overall_recall, 2))

    print '\tf-score: %s' % str(round(2*(overall_precision*overall_recall)/(overall_precision+overall_recall), 2))

    print '\n\t##### performance by slot type #####'
    for slot_type in slots:
        print '\n\tslot type: %s' % slot_type
        assessment_corrected_entries = assessment_corrected_entries_by_type[slot_type]
        evaluated_entry_num = evaluated_entry_num_by_type[slot_type]

        try:
            slot_filler_precision = 1.0*slot_filler_correct_entry_by_type[slot_type]/evaluated_entry_num
        except ZeroDivisionError:
            slot_filler_precision = 0
        try:
            provenance_precision = 1.0*provenance_correct_entry_by_type[slot_type]/evaluated_entry_num
        except ZeroDivisionError:
            provenance_precision = 0
        try:
            overall_precision = 1.0*overall_correct_entry_by_type[slot_type]/evaluated_entry_num
        except ZeroDivisionError:
            overall_precision=0
        try:
            overall_recall = 1.0*overall_correct_entry_by_type[slot_type]/assessment_corrected_entries
        except ZeroDivisionError:
            overall_recall = 0

        try:
            f_score = 2*(overall_precision*overall_recall)/(overall_precision+overall_recall)
        except ZeroDivisionError:
            f_score = 0

        print '\t\tgold entries: %s' % str(assessment_corrected_entries)

        print '\t\tevaluated entries: %s' % str(evaluated_entry_num)

        print '\t\tcorrect slot filler entries: %s, precision: %s' % (str(slot_filler_correct_entry_by_type[slot_type]),
                                                          str(round(slot_filler_precision, 2)))
        print '\t\tcorrect provenance entries %s, precision: %s' % (str(provenance_correct_entry_by_type[slot_type]),
                                                                    str(round(provenance_precision, 2)))
        print '\t\toverall correct: %s, precision: %s' % (str(overall_correct_entry_by_type[slot_type]),
                                                      str(round(overall_precision, 2)))
        print '\t\toverall recall: %s' % str(round(overall_recall, 2))

        print '\t\tf-score: %s' % str(round(f_score, 2))

    return

if __name__ == "__main__":
    tab_path = '../../data/ChineseSF_runs/RPI_BLENDER1'

    evaluate_runs(tab_path)


