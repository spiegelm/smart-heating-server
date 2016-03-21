"""
Copyright 2016 Michael Spiegel, Wilhelm Kleiminger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from rest_framework import serializers
from rest_framework.reverse import reverse


class HierarchicalHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    """
    Hyperlinked identity field for hierarchical urls.

    Calls `get_recursive_pks` on the associated object to collect its parent primary
    keys required to build the hierarchical URL.
    """
    def get_url(self, obj, view_name, request, format):
        args = obj.get_recursive_pks()
        return reverse(view_name, args=args, request=request, format=format)
