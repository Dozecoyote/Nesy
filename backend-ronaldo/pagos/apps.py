from django.apps import AppConfig


class PagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pagos'

    def ready(self):
        import pagos.signals
        from pagos.signals import signal_transferencia, transferencia

        signal_transferencia.connect(transferencia)