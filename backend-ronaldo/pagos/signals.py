# myapp/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from .models import Transaction, Balance
from django.db.transaction import rollback, commit

signal_transferencia = Signal()

@receiver(post_save, sender=Transaction)
def after_saving_instance(sender, instance, created, **kwargs):

    if created:
        print(f"Instancia creada: {instance.__dict__}")
        try:
            cuenta_usuario = Balance.objects.get(user_id = instance.user_id)
        except Balance.DoesNotExist:
            # Manejo de la situación cuando no se encuentra el objeto
            print("no existe")

        try:
            commit()
                # pago
            if instance.type_id.id == 1 or instance.type_id.id == 4:
                cuenta_usuario.balance -= instance.amount
                cuenta_usuario.save()

            elif instance.type_id.id == 2:
                # recarga
                cuenta_usuario.balance += instance.amount
                cuenta_usuario.save()

            elif instance.type_id.id == 3:
                # retiro
                pass

        except:
            rollback()
            instance.status = "E"
            instance.save()

        instance.status = "X"
        instance.save()



def transferencia(sender, **kwargs):

    data = kwargs.get('data', None)

    usuario = data['usuario']
    cantidad = data['cantidad']

    try:
        commit()
        usuario.balance += cantidad
        usuario.save()
    except:
        rollback()

    
   
        
        