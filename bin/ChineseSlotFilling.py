__author__ = 'boliangzhang'

import sys
import os

from RPISlotFilling.slot_filling.ChineseSlotFilling import ChineseSlotFilling


if len(sys.argv) != 3:
    print('Incorrect number of arguments.')
    print('ChineseSlotFilling requires 2 arguments:')
    print('\t1) LDC format slot filling queries.')
    print('\t2) Path to output result and visualization result.')
    exit()

path = os.path.dirname(os.path.realpath(__file__))

query_path = os.path.join(path, sys.argv[1])
if not os.path.exists(query_path):
    print(sys.argv[1]+' not exist')

output_path = os.path.join(path, sys.argv[2])
if not os.path.exists(output_path):
    print(sys.argv[2]+' not exist')

cn_sf = ChineseSlotFilling()

cn_sf.get_answer(query_path)

cn_sf.export_answer(os.path.join(output_path, 'cn_sf_result.tab'))

cn_sf.visualize(os.path.join(output_path, 'cn_sf_result.html'))
