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
