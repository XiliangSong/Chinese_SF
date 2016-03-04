import os
from subprocess import Popen, PIPE


path = os.path.dirname(os.path.abspath(__file__))

# install JCC which is required by Pylucene
jcc_path = os.path.join(path, 'externals/pylucene-4.10.1-1/jcc')

os.chdir(jcc_path)

print('Building JCC...')
p = Popen(['python', 'setup.py', 'build'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)
print('Done')

print('Installing JCC...')
java_home = os.environ['JAVA_HOME']
jcc_clang_error_fix = 'c++ -Wl, -dynamiclib -undefined dynamic_lookup build/temp.macosx-10.10-intel-2.7/jcc/sources/jcc.o build/temp.macosx-10.10-intel-2.7/jcc/sources/JCCEnv.o -o build/lib.macosx-10.10-intel-2.7/libjcc.dylib -L' + java_home + '/jre/lib -ljava -L' + java_home + '/jre/lib/server -ljvm -Wl,-rpath -Wl,' + java_home + '/jre/lib -Wl,-rpath -Wl,' + java_home + '/jre/lib/server -Wl,-S -install_name @rpath/libjcc.dylib -current_version 2.21 -compatibility_version 2.21'
p = Popen(jcc_clang_error_fix, stdout=PIPE, stderr=PIPE, shell=True)
p.communicate()
p = Popen(['python', 'setup.py', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)

input = raw_input('Make sure no error occurs and success message is shown. (press ENTER to continue)')

# install pylucene
print('Building Pylucene (This takes a while)...')
pylucene_path = os.path.join(path, 'externals/pylucene-4.10.1-1')
os.chdir(pylucene_path)

p = Popen(['make'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)

input = raw_input('Make sure no error occurs and success message is shown. (press ENTER to continue)')

print('Installing Pylucene...'),
p = Popen(['make', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print(stdout)
print(stderr)

print 'If no error occurs and success message is shown, pylucene is install successfully.'
