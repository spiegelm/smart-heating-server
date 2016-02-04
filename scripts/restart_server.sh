. ~/env/bin/activate
set -e # Abort on error
set -u # Error on uninitialised variable usage
set -v # Verbose
fuser -k 8000/tcp
pip install -r requirements.txt
./manage.py migrate
./manage.py test
nohup ./manage.py runserver 0:8000 &
