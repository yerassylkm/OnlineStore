"""
Forms for registration and login (MongoDB users).
"""
from django import forms
from django.contrib.auth.hashers import make_password

# Registration: name, surname, email, password (per project schema)
class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100, label="Имя")
    surname = forms.CharField(max_length=100, label="Фамилия")
    email = forms.EmailField(label="Email или номер телефона")
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=6,
        label="Пароль"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Подтвердите пароль"
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        from core.mongodb import users_collection
        if users_collection().find_one({"email": email}):
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password_confirm"):
            raise forms.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def save_mongo(self):
        """Save user to MongoDB (project schema: name, surname, email, password)."""
        from core.mongodb import users_collection
        doc = {
            "name": self.cleaned_data["name"],
            "surname": self.cleaned_data["surname"],
            "email": self.cleaned_data["email"],
            "password": make_password(self.cleaned_data["password"]),
        }
        r = users_collection().insert_one(doc)
        return str(r.inserted_id)


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Пароль")
