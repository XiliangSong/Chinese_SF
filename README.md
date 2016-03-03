# RPI BLENDER Chinese Slot Filling System
---------------------------

This is RPI BLENDER Chinese slot filling system. Definition of slot filling: Slot filling aims at collecting from a large-scale multi-source corpus the values (“slot fillers”) for certain attributes (“slot types”) of a query entity, which is a person or some type of organization.[1]

[1] Dian Yu, Hongzhao Huang, Taylor Cassidy, Heng Ji, Chi Wang, Shi Zhi, Jiawei Han, Clare Voss and Malik Magdon-Ismail. The Wisdom of Minority: [Unsupervised Slot Filling Validation based on Multi-dimensional Truth-Finding.](http://nlp.cs.rpi.edu/paper/mtm.pdf) (COLING 2014)

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

Currently only KBP SF format query input is accepted. Examples are provided in 'example/'.

Use command 

```
python RPISlotFilling/slot_filling/ChineseSlotFilling.py <input_query_file_path> <output_directory>
```

Please notice that the first argument is query file **path** and the second argument is a **directory**. Two results will be created under output directory: 'cn_sf_result.tab' in KBP SF format and 'cn_sf_result.html'.




## License

This work was supported by the US ARL  NS-CTA  No.  W911NF-09-2-0053,  DARPA DEFT No. FA8750-13-2-0041, NSF Awards IIS-1523198,  IIS-1017362, IIS-1320617, IIS-1354329 and  HDTRA1-10-1-0120, gift awards from IBM,  Google,  Disney  and  Bosch.  The  views  and conclusions contained in this document are those of the  authors  and  should  not  be  interpreted  as  representing  the  official  policies,  either  expressed  or implied,  of  the  U.S.  Government.   The  U.S. Government  is  authorized  to  reproduce  and  distribute reprints  for  Government  purposes  notwithstanding any copyright notation here on.

## Developer
   * Boliang Zhang [zhangb8@rpi.edu]