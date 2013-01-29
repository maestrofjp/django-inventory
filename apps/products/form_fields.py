# -*- encoding: utf-8 -*-
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.datastructures import MultiValueDict, MergeDict

from models import ProductAttributeValue

class CSWItem(StrAndUnicode):
    """ItemCategory record for the CategoriesSelectWidget
    
        The widget will display all available categories. While building the
        html code, this pseydo-object will represent each Category record to
        be rendered.
    """

    def __init__(self, parent, obj):
        self._parent = parent
        self._obj = obj

    def __unicode__(self):
        return unicode(self._obj)

    @property
    def did(self):
        """div-id of this selection element
        """
        return mark_safe("%s-%d" %(self._parent._name, self._obj.id))

    @property
    def id(self):
        """Record-id (aka. value) for this item
        """
        return mark_safe(str(self._obj.id))

    @property
    def name(self):
        """ID of the parent field
        """
        return self._parent._name

class CSWItem_Main(CSWItem):
    """Instance of first-level category in the page
    
        It can be iterated to find 2nd level categories
    """
    def standalones(self):
        """Returns non-bundled sub-categories
        """
        for subcat in self._parent._queryset.filter(parent=self._obj, ):
            yield CSWItem_Sub(self._parent, subcat)

class CSWItem_Sub(CSWItem):
    """Instance of second-level category
    """
    pass

class CSWRenderer(StrAndUnicode):
    # parent_field = 'parent'

    def __init__(self, queryset, name, value, attrs):
        self._queryset = queryset
        self._name = name
        self._value = value or []
        self.attrs = attrs

    def __unicode__(self):
        return "<!-- CSWRenderer: %s with %d vals -->" % (self._name, len(self._value))

    def __iter__(self):
        for icat in self._queryset.filter(parent__isnull=True):
            yield CSWItem_Main(self, icat)

    def render(self):
        return mark_safe(unicode(self))

class CategoriesSelectWidget(forms.widgets.Select):
    """Select widget of ItemCategory entries, in 3-level selectors

        @param queryset must be the full dataset of *all three* levels
            of item categories to use. It will be filter()ed accordingly
            for each level
    """

    def __init__(self, queryset=None, choices=(), *args, **kwargs):
        super(CategoriesSelectWidget, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.choices = choices # but don't render them to list
        self._renderer = None

    def subwidgets(self, name, value, attrs=None, choices=()):
        for w in self.get_renderer(name, value, attrs, choices):
            yield w

    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices).render()

    def get_renderer(self, name, value, attrs=None, choices=()):
        """ Rendering of this widget MUST be done with some template loops

            We do NOT support direct text rendering like `{{ this_field }}`, but
            instead mandate a loop like `{% for cat1 in this_field %} {{ cat1.title }}`
        """
        if not self._renderer:
            final_attrs = self.build_attrs(attrs, name=name)
            if isinstance(self.choices, forms.models.ModelChoiceIterator):
                # The ModelChoiceIterator is a *very* slow object, we must extract
                # its queryset and use it directly
                self.queryset = self.choices.queryset
                self.choices = ()
            self._renderer = CSWRenderer(self.queryset, name, value, final_attrs)
        return self._renderer


#eof
