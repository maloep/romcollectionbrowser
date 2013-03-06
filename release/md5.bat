@echo off
REM Drag a file onto me to create a .md5 hash
python -c "import hashlib,sys;open('%%s.md5'%%sys.argv[1],'wt',encoding='UTF-8').write(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest())" %1