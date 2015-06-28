import os

from subprocess import Popen, PIPE

path = os.path.dirname(os.path.realpath(__file__))

# install JCC which is required by Pylucene
jcc_path = os.path.join(path, 'externals/pylucene-4.10.1-1/jcc')

os.chdir(jcc_path)

print('Building JCC...'),
p = Popen(['python', 'setup.py', 'build'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr:
    print stderr
    exit()
print('Done')

print('Installing JCC...'),
p = Popen(['python', 'setup.py', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr:
    print stderr
    exit()
print('Done')

# install pylucene
pylucene_path = os.path.join(path, 'externals/pylucene-4.10.1-1')
os.chdir(pylucene_path)

print('Building Pylucene...'),
p = Popen(['make'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr:
    print stderr
    exit()
print('Done')

print('Installing Pylucene...'),
p = Popen(['make', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr:
    print stderr
    exit()
print('Done')

print('Installing dependency packages...'),
os.chdir(path)
p = Popen(['python', 'setup.py', 'install'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
if stderr:
    print stderr
    exit()
print('Done')