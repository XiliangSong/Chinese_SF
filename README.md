# RPI BLENDER Chinese Slot Filling System
---------------------------

This is RPI BLENDER Chinese slot filling system. Definition of slot filling: Slot filling aims at collecting from a large-scale multi-source corpus the values (“slot fillers”) for certain attributes (“slot types”) of a query entity, which is a person or some type of organization.[1]

[1] Dian Yu, Hongzhao Huang, Taylor Cassidy, Heng Ji, Chi Wang, Shi Zhi, Jiawei Han, Clare Voss and Malik Magdon-Ismail. The Wisdom of Minority: [Unsupervised Slot Filling Validation based on Multi-dimensional Truth-Finding.](http://nlp.cs.rpi.edu/paper/mtm.pdf) (COLING 2014)

## Example
* System's input is a XML file.
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
</kbpslotfill>
```
* Outputs are KBP slot filling '.tab' file and a HTML file.
```
SF14_CMN_TRAINING_001	per:age	SYS	xin_cmn_20040714.0019:58-174	82	xin_cmn_20040714.0019:171-172	1
SF14_CMN_TRAINING_001	per:country_of_death	SYS	xin_cmn_20071015.0207:216-219,xin_cmn_20040714.0019:58-174	中国	xin_cmn_20071015.0207:216-217	1
...
```

## Install

1. Clone the project.

2. Download external softwares and KBP Chinese slot filling source 

    * data and externals: [http://blender04.cs.rpi.edu/~zhangb8/ChineseSlotFilling/dependencies/data_and_externals.zip](http://blender04.cs.rpi.edu/~zhangb8/ChineseSlotFilling/dependencies/)

    * KBP_Chinese_Source_Corpus: [http://blender04.cs.rpi.edu/~zhangb8/ChineseSlotFilling/dependencies/2014_KBP_Chinese_Source_Corpus_extracted.tar.gz](http://blender04.cs.rpi.edu/~zhangb8/ChineseSlotFilling/dependencies/)
    
    * Put folder 'data' and 'externals' in the root directory.
    
    * Extract '2014_KBP_Chinese_Source_Corpus_extracted.tar.gz' and move it under 'data/' directory.

3. Required Dependencies:  

    * JDK 7 (1.7) or higher.  
    * Apache Ant
    * Python 2.7
    * GCC
   
    * Python packages:
        * pexpect >= 2.4
        * xmltodict >= 0.4.6
        * jianfan >= 0.0.2
        * jinja2 >= 2.7.3
        * python-Levenshtein >= 0.12

4. Environment and dependencies setting:  

	* Pylucene requires ant. If ant is not at '/usr/bin/ant', please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'ANT' to where you installed ant.  

	* Default python path is '/usr/bin/python'. If you are using Python virtual environment, please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'PREFIX_PYTHON' to the directory of your python virtual environment. If you installed python in other directory, change 'PREFIX_PYTHON' in 'externals/pylucene-4.10.1-1/Makefile' to directory where your python installed.
    
    * ANT_HOME=(ANT directory)
    * JAVA_HOME=(Java directory)
    * JCC_JDK=$JAVA_HOME

5. Install pylucene

    Use command:
    
    ```
    python install_pylucene.py
    ```

6. Add Chinese_SF path to PYTHONPATH in bash profile. Use command
    ```
    export PYTHONPATH=$PYTHONPATH:<Chinese_SF path>
    ```

## Usage

Examples are provided in 'example/'.

Use command 

```
python RPISlotFilling/slot_filling/ChineseSlotFilling.py <input_query_file_path> <output_directory>
```

Please notice that the first argument is the **file** path and the second argument is a **directory** path. Two results will be created under output directory: 'cn_sf_result.tab' in KBP SF format and 'cn_sf_result.html'.

## Contact
   * Boliang Zhang [zhangb8@rpi.edu]