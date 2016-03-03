#encoding=utf-8
import io
import os


def load_triggers():
    triggers = dict()
    for file_name in os.listdir('../../data/triggers'):
        if file_name == ".DS_Store":
            continue
        f = io.open('../../data/triggers/'+file_name, 'r', -1, 'utf-8')
        triggers[file_name] = f.read().strip().splitlines()

    return triggers


def load_ppdb():
    ppdb = dict()

    threshold = 200000
    f = io.open('../../data/ppdb-1.0-lookup-all', 'r', -1, 'utf-8')
    counter = 0
    for line in f:
        if counter == threshold:
            break

        line = line.strip().split('|||')
        line = [item.strip() for item in line]
        try:
            ppdb[line[1]].add(line[2])
        except KeyError:
            ppdb[line[1]] = set([line[2]])

        counter += 1

    return ppdb

if __name__ == "__main__":
    triggers = load_triggers()
    ppdb = load_ppdb()

    new_trigger_num = 0
    orig_trigger_num = 0
    # trigger extension
    for trigger_type in triggers:
        orig_triggers = triggers[trigger_type]
        extended_triggers = set()
        for t in orig_triggers:
            try:
                extended_triggers = extended_triggers.union(ppdb[t])
            except KeyError:
                continue

        if not extended_triggers:
            print 'not extended triggers found for %s' % trigger_type
            continue

        f = io.open('../../data/extended_triggers/'+trigger_type, 'w', -1, 'utf-8')
        f.write('\n'.join(extended_triggers.difference(orig_triggers)))
        f.close()

        f = io.open('../../data/extended_triggers/'+trigger_type+'.diff', 'w', -1, 'utf-8')
        f.write(u'\n'.join(extended_triggers.difference(orig_triggers)))
        f.close()

        print '#%s:' % trigger_type
        print u'\n'.join(extended_triggers.difference(orig_triggers)),
        print u'\n'

        new_trigger_num += len(extended_triggers.difference(orig_triggers))
        orig_trigger_num += len(orig_triggers)

    print '%s original triggers.' % orig_trigger_num
    print '%s new triggers are populated.' % new_trigger_num