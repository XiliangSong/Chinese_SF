__author__ = 'boliangzhang'

class Evidence(object):
    def __init__(self, doc_id, query_id, trigger, sent_text, sent_id, parse_result=None):
        self.doc_id = doc_id
        self.query_id = query_id
        self.trigger = trigger
        self.sent_text = sent_text
        self.sent_id = sent_id
        self.parse_result = parse_result
