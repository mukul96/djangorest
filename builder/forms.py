from django import forms
class LoginForm(forms.Form):
    email= forms.EmailField(max_length = 25)
    password = forms.CharField(widget = forms.PasswordInput)


class ProjectForm(forms.Form):
	name=forms.CharField(max_length=100)
	address=forms.CharField(max_length=100)
	current_expenses=forms.IntegerField()
	total_budget=forms.IntegerField()

class InventoryForm(forms.Form):
	inventory_name=forms.CharField(max_length=100)
	inventory_qty=forms.IntegerField()

'''class TransactionForm(forms.Form):
	RELEVANCE_CHOICES = (
    (1, _("Increase")),
    (0, _("Decrease"))
)	inc_dec=forms.ChoiceField(choices = RELEVAMCE_CHOICES, label="", initial='', widget=forms.Select(), required=True)
	delta=forms.IntegerField()
	comment=forms.CharField(max_length=100)'''
