from django import forms
from .models import Host, Idc, Cabinet, HostGroup


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = '__all__'
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'idc': forms.Select(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'os': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_model': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_num': forms.TextInput(attrs={'class': 'form-control'}),
            'memory': forms.TextInput(attrs={'class': 'form-control'}),
            'disk': forms.TextInput(attrs={'class': 'form-control'}),
            'sn': forms.TextInput(attrs={'class': 'form-control'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class IdcForm(forms.ModelForm):
    class Meta:
        model = Idc
        fields = '__all__'
        widgets = {
            'ids': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'tel': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'jigui': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_range': forms.TextInput(attrs={'class': 'form-control'}),
            'bandwidth': forms.TextInput(attrs={'class': 'form-control'}),
            'memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CabinetForm(forms.ModelForm):
    class Meta:
        model = Cabinet
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'idc': forms.Select(attrs={'class': 'form-control'}),
            'desc': forms.TextInput(attrs={'class': 'form-control'}),
        }


class HostGroupForm(forms.ModelForm):
    class Meta:
        model = HostGroup
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'desc': forms.TextInput(attrs={'class': 'form-control'}),
        }