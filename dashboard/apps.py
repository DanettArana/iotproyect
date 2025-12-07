from django.apps import AppConfig
import os
import sys


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # Iniciar cliente MQTT automáticamente cuando Django esté listo
        # Solo iniciar en el proceso principal (evitar doble inicio por reloader)
        # En Windows, verificar si estamos ejecutando runserver
        is_runserver = 'runserver' in sys.argv
        is_main_process = (
            os.environ.get('RUN_MAIN') == 'true' or 
            (os.name == 'nt' and is_runserver) or
            not os.environ.get('RUN_MAIN')  # Si no está definido, asumir proceso principal
        )
        
        if is_main_process:
            try:
                import threading
                # Iniciar en un thread separado para no bloquear
                def start_mqtt():
                    try:
                        from .mqtt_client import run
                        run()
                    except Exception as e:
                        print(f"Error al iniciar cliente MQTT: {e}")
                        import traceback
                        traceback.print_exc()
                
                thread = threading.Thread(target=start_mqtt, daemon=True)
                thread.start()
            except Exception as e:
                print(f"Error al configurar cliente MQTT: {e}")
                import traceback
                traceback.print_exc()

