# -*- encoding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from generic_views.forms import DetailForm, InlineModelForm
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from inventory.models import Inventory

from models import PurchaseRequest, PurchaseRequestItem, PurchaseOrder, \
                   PurchaseOrderItem, Movement
from common.models import Location

#TODO: Remove auto_add_now from models and implement custom save method to include date

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        exclude = ('active',)


class PurchaseRequestForm_view(DetailForm):
    class Meta:
        model = PurchaseRequest
        exclude = ('active',)


class PurchaseRequestItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestItem


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        exclude = ('active',)


class PurchaseOrderForm_view(DetailForm):
    class Meta:
        model = PurchaseOrder
        exclude = ('active',)


class PurchaseOrderItemForm(forms.ModelForm):
    item_template = AutoCompleteSelectField('product')
    class Meta:
        model = PurchaseOrderItem
        exclude = ('active',)

class PurchaseOrderItemForm_inline(InlineModelForm):
    item_template = AutoCompleteSelectField('product')
    class Meta:
        model = PurchaseOrderItem
        exclude = ('active',)


class PurchaseOrderWizardItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PurchaseOrderWizardItemForm, self).__init__(*args, **kwargs)
        if 'item' in self.initial:
            self.fields['template_id'].initial = self.initial['item'].item_template.id
            self.fields['name'].initial = self.initial['item'].item_template
            self.fields['supplier'].choices = self.initial['item'].item_template.suppliers.all().values_list('id', 'name')
            self.fields['qty'].initial = self.initial['item'].qty

    template_id = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField(label=_(u'Name'), required=False, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    supplier = forms.ChoiceField(label=_(u'Suppliers'))
    qty = forms.CharField(label=_(u'Qty'))


class PurchaseOrderItemTransferForm(forms.Form):
    purchase_order_item_id = forms.CharField(widget=forms.HiddenInput)
    purchase_order_item = forms.CharField(label=_(u'Purchase order item'), widget=forms.TextInput(attrs={'readonly':'readonly'}))
    inventory = forms.ModelChoiceField(queryset = Inventory.objects.all(), help_text = _(u'Inventory that will receive the item.'))
    qty = forms.CharField(label=_(u'Qty received'))

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement

class MovementForm_view(DetailForm):
    class Meta:
        model = Movement

class _baseMovementForm(forms.ModelForm):
    items = AutoCompleteSelectMultipleField('item',)

class DestroyItemsForm(_baseMovementForm):
    """This form is registered whenever defective equipment is trashed (destroyed)
    """
    location_src = AutoCompleteSelectField('location', required=False)
    class Meta:
        model = Movement
        fields = ('name', 'date_act', 'origin', 'note', 'location_src', 'items')

class LoseItemsForm(_baseMovementForm):
    """ This form is completed whenever equipment is missing (lost/stolen)
    """
    location_src = AutoCompleteSelectField('location', required=False)
    class Meta:
        model = Movement
        fields = ('name', 'date_act', 'origin', 'note', 'location_src', 'items')

class MoveItemsForm(_baseMovementForm):
    """ Registered whenever equipment moves from one inventory to another
    """
    location_src = AutoCompleteSelectField('location', required=False)
    location_dest = AutoCompleteSelectField('location', required=False)

    class Meta:
        model = Movement
        fields = ('name', 'date_act', 'origin', 'note', 'location_src', 'location_dest',
                'items')

class RepairGroupForm(forms.Form):
    """Used to mark repairs (changes within group) of Items
    """
    name = forms.CharField(label=_("Protocol ID"),)

#eof