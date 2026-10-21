import importlib.util,time,re,sys
sys.argv=['x']
spec=importlib.util.spec_from_file_location('td','tools/test_death.py')
# reuse helpers without running the suite: exec only the helper part
src=open('tools/test_death.py').read(); helpers=src.split("for pl in DIR: R(f\"gamemode survival")[0]
ns={'__file__':'tools/test_death.py'}; exec(compile(helpers,'h','exec'),ns)
R=ns['R']; kit=ns['kit']; ground=ns['ground']; die=ns['die']; trails=ns['trails']; rec=ns['rec']; pick=ns['pick']
mode=sys.argv[1] if len(sys.argv)>1 else 'unload'
