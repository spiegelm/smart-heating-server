from rest_framework import serializers
from rest_framework.reverse import reverse


class HierarchicalHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        args = obj.get_recursive_pks()
        return reverse(view_name, args=args, request=request, format=format)

    # def get_object(self, queryset, view_name, view_args, view_kwargs):
    #     account = view_kwargs['account']
    #     slug = view_kwargs['slug']
    #     return queryset.get(account=account, slug=slug)