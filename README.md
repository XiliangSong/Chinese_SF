# RPI BLENDER Chinese Slot Filling System
---------------------------

This is RPI BLENDER Chinese slot filling system. Definition of slot filling: Slot filling aims at collecting from a large-scale multi-source corpus the values (“slot fillers”) for certain attributes (“slot types”) of a query entity, which is a person or some type of organization.[1]

[1] Dian Yu, Hongzhao Huang, Taylor Cassidy, Heng Ji, Chi Wang, Shi Zhi, Jiawei Han, Clare Voss and Malik Magdon-Ismail. The Wisdom of Minority: Unsupervised Slot Filling Validation based on Multi-dimensional Truth-Finding. (COLING 2014)

## Example
* The system takes KBP slot filling query format xml file as input.
```xml
<?xml version="1.0" encoding="utf-8"?>
<kbpslotfill>
  <query id="SF14_CMN_TRAINING_001">
    <name>郭全宝</name>
    <enttype>PER</enttype>
    <docid>cmn-NG-4-76762-9532908</docid>
    <beg>2536</beg>
    <end>2538</end>
  </query>
  <query id="SF14_CMN_TRAINING_006">
    <name>华泰财产保险股份有限公司</name>
    <enttype>ORG</enttype>
    <docid>CNS_CMN_20100325.1032</docid>
    <beg>478</beg>
    <end>489</end>
  </query>
</kbpslotfill>
```
* Outputs are KBP slot filling '.tab' file and HTML file.

## How To Install
1. Clone the project.
2. Requirements:  
	JDK 7 (1.7) or higher.  
	Ant  
	Python 2.7
3. Environment variables setting:
	a. Pylucene requires ant. If ant is not at '/usr/bin/ant', please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'ANT' to where you installed ant.  
	b. Default python path is '/usr/bin/python', if you are using Python virtual environment or you installed python in other directory, please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'PREFIX_PYTHON' to directory of your python or python virtual environment.




## License

RPI BLENDER Chinese Slot Filling is licensed under the GNU General Public License (v2 or later). Note that this is the /full/ GPL, which allows many free uses, but not its use in distributed proprietary software.

## Developer
   * Boliang Zhang [zhangb8@rpi.edu]