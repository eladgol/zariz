"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

class FpasswordForm(PasswordResetForm):
    email = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    class Meta:
        model = User
        fields = ("email")
        print("FpasswordForm, Hello!!!!!!!!!!!!!!!! ")
    def clean_email(self):
        email = self.cleaned_data['email']
        print("FpasswordForm!!!!!!@222222!!!!!, Hello!!!!!!!!!!!!!!!!")
        # if function_checkemaildomain(email) == False:
        #     raise forms.ValidationError("Untrusted email domain")
        # elif function_checkemailstructure(email)==False:
        #     raise forms.ValidationError("This is not an email adress.")

        return email
    def get_users(self, email):
        print("FpasswordForm!!!!!!@3333333!!!!!, He")
        return (super().get_users(email))
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm

# noinspection PyClassHasNoInit
# class PasswordResetForm(BasePasswordResetForm):
    # """A self-reset form for users."""

    # def save(self, domain_override=None, subject_template_name='accounts/password_reset_subject.txt',
    #          email_template_name='accounts/password_reset_email.txt', use_https=False,
    #          token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None,
    #          extra_email_context=None):
    #     """Override the default in order to return the UID and token for use in the view. This also differs from the
    #     default behavior by working with one user at a time.
    #     # :rtype: list[str]
    #     # """

    #     # # Get the email. That's why we're here.
    #     # email = self.cleaned_data["email"]

    #     # # Find the user.
    #     # try:
    #     #     user = user_model.objects.get(email=email)
    #     # except user_model.DoesNotExist:
    #     #     return None, None

    #     # # Generate token and UID.
    #     # token = token_generator.make_token()
    #     # uid = urlsafe_base64_encode(force_bytes(user.pk))

    #     # # Get site info.
    #     # if domain_override:
    #     #     site_title = domain = domain_override
    #     # else:
    #     #     current_site = request.site
    #     #     site_title = current_site.name
    #     #     domain = current_site.domain

    #     # # Create the template context.
    #     # context = {
    #     #     'domain': domain,
    #     #     'email': email,
    #     #     'protocol': 'https' if use_https else 'http',
    #     #     'site_title': site_title,
    #     #     'token': token,
    #     #     'uid': uid,
    #     #     'user': user,
    #     # }

    #     # if extra_email_context is not None:
    #     #     context.update(extra_email_context)

    #     # # Send the email. 
    #     # # noinspection PyUnusedLocal
    #     # try:
    #     #     self.send_mail(
    #     #         subject_template_name,
    #     #         email_template_name,
    #     #         context,
    #     #         from_email,
    #     #         email
    #     #     )
    #     # except (SMTPAuthenticationError, SocketError) as e:
    #     #     # TODO: Need to deal with email errors.
    #     #     pass

    #     # # Return the token and uid for use in the view.
    #     # return token, uid