from django.db import models

# Create your models here.

class Users(models.Model):

    id = models.UUIDField(primary_key=True)
    curp = models.TextField(max_length=255, null=True)
    email = models.TextField(max_length=55)
    name = models.TextField(max_length=255)
    surnames = models.TextField(max_length=255, null=True)
    password = models.TextField(max_length=255)
    ine = models.TextField(max_length=255, null=True)
    photo = models.TextField(max_length=255, null=True)
    stripe = models.TextField(max_length=255, null=True)

    class Meta:
        db_table = 'users'

class TypeTransaction(models.Model):

    types = {
        "R" : "recarga",
        "T" : "transferencia",
        "RE" : "retiro",
        "P": "pago"
    }

    id = models.AutoField(primary_key=True)
    type = models.TextField(max_length=2, choices=types)

    class Meta:
        db_table = 'typeTransaction'

class Transaction(models.Model):

    STATUS_CHOICES = [
        ("E", "error"),
        ("X", "exitoso"),
        ("P", "en proceso")
    ]

    id = models.BigAutoField(primary_key=True)
    date = models.DateField(auto_now=True)
    amount = models.IntegerField()
    status = models.TextField(max_length=2, choices=STATUS_CHOICES, default="P")
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="usuario_id")
    user_trans_id = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, default=None, related_name="usuario_transferencia")
    type_id = models.ForeignKey(TypeTransaction, on_delete=models.PROTECT)

    class Meta:
        db_table = 'transactions'

class Balance(models.Model):

    id = models.BigAutoField(primary_key=True)
    balance = models.IntegerField(default=0)
    last_day = models.DateField(auto_now=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'balance'
    
class Roles(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.TextField(max_length=20)

    class Meta:
        db_table = 'roles'

class UserRoles(models.Model):

    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    role_id = models.ForeignKey(Roles, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_roles'

class Qr(models.Model):

    id = models.AutoField(primary_key=True)
    qr = models.TextField()
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'qr'