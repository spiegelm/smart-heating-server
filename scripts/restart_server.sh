. ~/env/bin/activate
set -v
fuser -k 8000/tcp
./manage.py migrate
./manage.py test
nohup ./manage.py runserver 0:8000 &
