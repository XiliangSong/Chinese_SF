__author__ = 'boliangzhang'


class Query(object):
    def __init__(self, et):
        self.id = ""
        self.name = ""
        self.entity_type = ""
        self.doc_id = ""
        self.beg = ""
        self.end = ""
        self.from_et(et)

    def from_et(self, et):
        self.id = et.get('id')
        self.name = et.find('name').text
        self.entity_type = et.find('enttype').text
        self.doc_id = et.find('docid').text
        self.beg = int(et.find('beg').text)
        self.end = int(et.find('end').text)

    def __lt__(self, other):
        return not other < self.id

    @staticmethod
    def find_query_by_id(queries, q_id):
        for q in queries:
            if q.id == q_id:
                return q
        return None