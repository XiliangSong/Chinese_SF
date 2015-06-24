__author__ = 'boliangzhang'

import re


def remove_pos_tag(sentence):
    return re.sub('\|\w+', '', sentence.strip())


def remove_xml_tag(sentence):
    return re.sub('<[^>]*>', '', sentence)


def remove_space_linebreak(sentence):
    return sentence.replace('\n', '').replace(' ', '')


def remove_doc_noise(sentence):
    def find_substring(sentence, beg, end):
        beg_index = sentence.find(beg)
        end_indxe = sentence.find(end) + len(end)

        if beg_index == -1 or end_indxe == -1:
            return ''

        return sentence[beg_index: end_indxe]

    # in doc like cmn-ng-31-111717-11957288, text will be included in a <quote> tag
    sentence = sentence.replace('<quote', '')
    sentence = sentence.replace(find_substring(sentence, '<dateline>', '</dateline>'), '')
    sentence = sentence.replace(find_substring(sentence, '<headline>', '</headline>'), '')
    sentence = sentence.replace(find_substring(sentence, '<docid>', '</docid>'), '')
    sentence = sentence.replace(find_substring(sentence, '<datetime>', '</datetime>'), '')
    sentence = sentence.replace(find_substring(sentence, '<doctype', '</doctype>'), '')
    sentence = sentence.replace(find_substring(sentence, '<postdate>', '</postdate>'), '')
    sentence = sentence.replace(find_substring(sentence, '<poster>', '</poster>'), '')

    return sentence


