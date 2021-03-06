# Copyright 2016 Michael Spiegel, Wilhelm Kleiminger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

. ~/env/bin/activate
set -e # Abort on error
set -u # Error on uninitialised variable usage
set -v # Verbose
fuser -k 8000/tcp
pip install -r requirements.txt
./manage.py migrate
./manage.py test
nohup ./manage.py runserver 0:8000 &
