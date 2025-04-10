from django import forms
from .models import Drug, DrugGroup, SideEffect


class AddDrugGroupForm(forms.ModelForm):
    class Meta:
        model = DrugGroup
        fields = '__all__'


class AddDrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = '__all__'


class DisplaySideEffectsForm(forms.Form):
    display_method = forms.ChoiceField(label="Выберите способ отображения побочек")

    def __init__(self, *args, **kwargs):
        super(DisplaySideEffectsForm, self).__init__(*args, **kwargs)
        choices = [('all', 'Показать всё')]
        drugs = Drug.objects.all()
        choices += [(str(drug.id), drug.name) for drug in drugs]
        self.fields['display_method'].choices = choices


class UpdateSideEffectProbabilityForm(forms.Form):
    side_effect = forms.ChoiceField(label="Выберите побочный эффект")
    probability = forms.FloatField(
        label="Коэффициент появления",
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )

    def __init__(self, *args, **kwargs):
        super(UpdateSideEffectProbabilityForm, self).__init__(*args, **kwargs)
        choices = [(str(se.id), se.name) for se in SideEffect.objects.all()]
        self.fields['side_effect'].choices = choices


class AddSideEffect(forms.Form):
    name = forms.CharField(
        label='Название побочного эффекта',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
