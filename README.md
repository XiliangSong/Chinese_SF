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

2. Download external softwares and KBP Chinese slot filling source 

KBP_Chinese_Source_Corpus: https://www.dropbox.com/s/wilog3m7ntr345z/2014_KBP_Chinese_Source_Corpus_extracted.tar.gz?dl=1

data and externals: https://www.dropbox.com/s/hyofbax21pjeb7z/data_%26_externals.zip?dl=1

Put folder 'data' and 'externals' in the root directory. And please extract '2014_KBP_Chinese_Source_Corpus_extracted.tar.gz' and move it to 'data/' directory.

3. Required Development Tools:  

   * JDK 7 (1.7) or higher.  
   * Ant  
   * Python 2.7

4. Environment variables setting:  

	* Pylucene requires ant. If ant is not at '/usr/bin/ant', please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'ANT' to where you installed ant.  

	* Default python path is '/usr/bin/python'. If you are using Python virtual environment, please go to 'externals/pylucene-4.10.1-1/Makefile' and change 'PREFIX_PYTHON' to the directory of your python virtual environment. If you installed python in other directory, change 'PREFIX_PYTHON' in 'externals/pylucene-4.10.1-1/Makefile' to directory where your python installed.

5. Install Chinese Slot Filling
Run 'python setup.py install' to install the package.

## Usage
Currently only KBP SF format query input is accepted.
In bin directory, use command 'python ChineseSlotFilling.py <input_query_file_path> <output_directory>'. Please notice that the second argument is a directory. Two results will be created under output directory: 'cn_sf_result.tab' is in KBP SF format and 'cn_sf_result.html' is a 




## License

This work was supported by the US ARL  NS-CTA  No.  W911NF-09-2-0053,  DARPA DEFT No. FA8750-13-2-0041, NSF Awards IIS-1523198,  IIS-1017362, IIS-1320617, IIS-1354329 and  HDTRA1-10-1-0120, gift awards from IBM,  Google,  Disney  and  Bosch.  The  views  and conclusions contained in this document are those of the  authors  and  should  not  be  interpreted  as  representing  the  official  policies,  either  expressed  or implied,  of  the  U.S.  Government.   The  U.S. Government  is  authorized  to  reproduce  and  distribute reprints  for  Government  purposes  notwithstanding any copyright notation here on.

## Developer
   * Boliang Zhang [zhangb8@rpi.edu]