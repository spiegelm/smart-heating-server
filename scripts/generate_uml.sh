#!/bin/bash
set -e # Exit script on error

./manage.py graph_models smart_heating > uml_class_diagram.dot
dot -Tpng uml_class_diagram.dot -o uml_class_diagram.png
# gnome-open uml_class_diagram.png
