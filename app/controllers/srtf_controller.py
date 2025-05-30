<<<<<<< HEAD
import heapq # Puede ser útil para manejar la cola de listos eficientemente

class SRTFController:
    @staticmethod
    def simular_srtf(procesos_iniciales):
        """
        Simula el algoritmo de planificación Shortest Remaining Time First (SRTF).

        Args:
            procesos_iniciales (list): Una lista de diccionarios, donde cada diccionario
                                     representa un proceso y debe contener las claves:
                                     'nombre' (str): Identificador del proceso.
                                     'llegada' (int): Tiempo de llegada del proceso.
                                     'duracion_original' (int): Duración total de CPU requerida.
                                     (También puede incluir 'restante' si ya está precalculado,
                                      pero se recalculará aquí por seguridad).

        Returns:
            list: Una lista de diccionarios, donde cada diccionario representa un segmento
                  de ejecución en el diagrama de Gantt. Cada segmento incluye:
                  'proceso' (str): Nombre del proceso.
                  'llegada' (int): Tiempo de llegada original del proceso.
                  'cpu_original' (int): Duración total original de CPU del proceso.
                  'comienzo' (int): Tiempo de inicio de este segmento de ejecución.
                  'final' (int): Tiempo de finalización de este segmento de ejecución.
                  'espera_final' (int): Tiempo total de espera del proceso.
                  'turnaround_final' (int): Tiempo total de turnaround del proceso.
        """
        if not procesos_iniciales:
            return []

        # Inicialización de variables y estructuras de datos
        tiempo_actual = 0
        procesos_completados_count = 0
        lista_segmentos_ejecucion = [] # Para el diagrama de Gantt

        # Copiar procesos para no modificar la entrada y añadir/estandarizar campos
=======
class SRTFController:
    """
    Controlador para simular el algoritmo de planificación Shortest Remaining Time First (SRTF).
    Este es el código que generé anteriormente, con la salida por segmentos.
    """
    @staticmethod
    def simular_srtf(procesos_iniciales):
        if not procesos_iniciales:
            return []

        tiempo_actual = 0
        procesos_completados_count = 0
        lista_segmentos_ejecucion = []

>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
        procesos = []
        for i, p_orig in enumerate(procesos_iniciales):
            p_copy = p_orig.copy()
            p_copy['id'] = p_orig.get('nombre', f"Proceso_{i+1}")
<<<<<<< HEAD
            # Asegurar que 'duracion_original' y 'restante' se basan en la duración de entrada
            duracion_key = 'duracion_original' if 'duracion_original' in p_orig else 'duracion'
            p_copy['duracion_original'] = p_orig[duracion_key]
            p_copy['restante'] = p_orig[duracion_key]
            
            # Campos para estadísticas finales
            p_copy['tiempo_finalizacion'] = 0
            p_copy['tiempo_espera_final'] = "Calc..." # Se calculará al final
            p_copy['turnaround_final'] = "Calc..."  # Se calculará al final
            procesos.append(p_copy)

        # Ordenar procesos por tiempo de llegada para manejar las entradas correctamente
        # Esto es solo para la consideración inicial, la cola de listos se manejará dinámicamente.
        # procesos.sort(key=lambda p: p['llegada']) # No es estrictamente necesario si se filtran llegados en cada paso

        # Diccionario para almacenar las estadísticas finales calculadas para cada proceso
        stats_finales_procesos = {p['id']: {} for p in procesos}

        # Bucle principal de la simulación
        while procesos_completados_count < len(procesos):
            # Filtrar procesos que han llegado y aún tienen tiempo restante (procesos listos)
=======
            duracion_key = 'duracion_original' if 'duracion_original' in p_orig else 'duracion'
            if duracion_key not in p_copy:
                 print(f"ADVERTENCIA (SRTFController): Proceso {p_copy.get('id')} no tiene clave de duración. Asumiendo 1.")
                 p_copy[duracion_key] = 1
            p_copy['duracion_original_calc'] = p_copy[duracion_key]
            p_copy['restante'] = p_copy[duracion_key]
            p_copy['tiempo_finalizacion_calc'] = 0
            p_copy['tiempo_espera_final_calc'] = "Calc..."
            p_copy['turnaround_final_calc'] = "Calc..."
            procesos.append(p_copy)

        stats_finales_procesos = {p['id']: {} for p in procesos}

        while procesos_completados_count < len(procesos):
>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
            procesos_listos_para_ejecutar = [
                p for p in procesos if p['llegada'] <= tiempo_actual and p['restante'] > 0
            ]

            if not procesos_listos_para_ejecutar:
<<<<<<< HEAD
                # Si no hay procesos listos, avanzar el tiempo hasta la llegada del próximo proceso
=======
>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
                tiempos_llegada_futuros = [
                    p['llegada'] for p in procesos if p['llegada'] > tiempo_actual and p['restante'] > 0
                ]
                if not tiempos_llegada_futuros:
<<<<<<< HEAD
                    # No hay más procesos por llegar o todos los que quedan ya llegaron pero no están listos (improbable si hay restantes)
                    # O todos los procesos han terminado.
                    break # Salir del bucle si no hay más trabajo o llegadas
                
                tiempo_actual = min(tiempos_llegada_futuros)
                continue # Re-evaluar en el nuevo tiempo_actual

            # Seleccionar el proceso con el menor tiempo restante de la cola de listos
            # Desempate: menor tiempo de llegada, luego por ID (nombre)
            procesos_listos_para_ejecutar.sort(key=lambda p: (p['restante'], p['llegada'], p['id']))
            proceso_actual_ejecutando = procesos_listos_para_ejecutar[0]

            # Determinar cuánto tiempo se ejecutará este proceso antes del próximo evento (fin o llegada)
            tiempo_inicio_segmento = tiempo_actual
            
            # Evento 1: El proceso actual termina
            tiempo_hasta_fin_proceso_actual = proceso_actual_ejecutando['restante']

            # Evento 2: Llega un nuevo proceso que podría ser más corto
            tiempo_hasta_proxima_llegada_relevante = float('inf')
            for p_futuro in procesos:
                if p_futuro['llegada'] > tiempo_actual and p_futuro['restante'] > 0:
                    # Solo nos importan las llegadas que ocurren antes de que el proceso actual termine por sí mismo
                    if p_futuro['llegada'] < tiempo_actual + tiempo_hasta_fin_proceso_actual:
                         tiempo_hasta_proxima_llegada_relevante = min(tiempo_hasta_proxima_llegada_relevante, p_futuro['llegada'] - tiempo_actual)
            
            # El tiempo de ejecución para este slot es el mínimo de estos eventos
            tiempo_ejecucion_este_slot = min(tiempo_hasta_fin_proceso_actual, tiempo_hasta_proxima_llegada_relevante)
            
            # Si no hay llegadas futuras antes de que termine el proceso actual,
            # tiempo_hasta_proxima_llegada_relevante será inf, así que se ejecutará hasta el fin.
            # Si tiempo_ejecucion_este_slot es 0 (ej. una llegada en tiempo_actual), se re-evaluará.
            # Aseguramos un avance mínimo si no hay eventos, o si el slot es 0 pero el proceso tiene trabajo.
            # La lógica de "if not procesos_listos_para_ejecutar" maneja el avance si CPU está idle.
            # Si el slot es 0, significa que en el próximo ciclo se re-evaluará con el nuevo proceso llegado.
            if tiempo_ejecucion_este_slot <= 0: # Forzar al menos 1 si es posible, o re-evaluar.
                # Si el proceso actual tiene restante y el slot es 0, es porque una llegada coincide.
                # El bucle re-evaluará. Si no hay llegadas y el slot es 0, algo está mal.
                # Por seguridad, si el proceso tiene restante, intentamos ejecutar por 1.
                # Pero la lógica de min(tiempo_hasta_fin, tiempo_hasta_llegada) debería ser correcta.
                # Si el slot es 0, es porque tiempo_actual == p_futuro['llegada'].
                # En este caso, no se ejecuta nada en este instante, se re-evalúa la cola de listos.
                 pass # El bucle se repetirá y seleccionará el proceso correcto (posiblemente el recién llegado)


            # Ejecutar el proceso
=======
                    break
                tiempo_actual = min(tiempos_llegada_futuros)
                continue

            procesos_listos_para_ejecutar.sort(key=lambda p: (p['restante'], p['llegada'], p['id']))
            proceso_actual_ejecutando = procesos_listos_para_ejecutar[0]

            tiempo_inicio_segmento = tiempo_actual
            tiempo_hasta_fin_proceso_actual = proceso_actual_ejecutando['restante']
            tiempo_hasta_proxima_llegada_relevante = float('inf')

            for p_futuro in procesos:
                if p_futuro['llegada'] > tiempo_actual and p_futuro['restante'] > 0:
                    if p_futuro['llegada'] < tiempo_actual + tiempo_hasta_fin_proceso_actual:
                        tiempo_hasta_proxima_llegada_relevante = min(tiempo_hasta_proxima_llegada_relevante, p_futuro['llegada'] - tiempo_actual)
            
            tiempo_ejecucion_este_slot = min(tiempo_hasta_fin_proceso_actual, tiempo_hasta_proxima_llegada_relevante)
            
            # Asegurar que el tiempo de ejecución sea al menos 1 si hay trabajo y no hay llegadas inminentes
            # o si el proceso puede terminar en este slot.
            if tiempo_ejecucion_este_slot <= 0 and tiempo_hasta_fin_proceso_actual > 0 :
                 # Esto puede pasar si una llegada coincide exactamente con tiempo_actual.
                 # En ese caso, no se ejecuta nada en este instante, se re-evalúa la cola.
                 # Si no hay llegadas (tiempo_hasta_proxima_llegada_relevante es inf),
                 # y el proceso tiene restante, el slot debe ser > 0.
                 # Si el slot es 0, el bucle se repetirá y seleccionará el proceso correcto.
                 # Para evitar un posible bucle si algo va mal y el tiempo no avanza,
                 # forzamos un avance de 1 unidad si no hay llegadas y el proceso tiene restante.
                 if tiempo_hasta_proxima_llegada_relevante == float('inf') and proceso_actual_ejecutando['restante'] > 0:
                     tiempo_ejecucion_este_slot = 1 # Ejecutar al menos 1 unidad
                 elif proceso_actual_ejecutando['restante'] > 0 : # Hay una llegada en tiempo_actual
                     pass # No ejecutar, dejar que el bucle re-evalúe
                 else: # Proceso sin restante, no debería estar aquí
                     continue
            
>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
            if tiempo_ejecucion_este_slot > 0:
                proceso_actual_ejecutando['restante'] -= tiempo_ejecucion_este_slot
                tiempo_actual += tiempo_ejecucion_este_slot
                tiempo_fin_segmento = tiempo_actual

                lista_segmentos_ejecucion.append({
                    'proceso': proceso_actual_ejecutando['id'],
                    'llegada': proceso_actual_ejecutando['llegada'],
<<<<<<< HEAD
                    'cpu_original': proceso_actual_ejecutando['duracion_original'],
                    'comienzo': tiempo_inicio_segmento,
                    'final': tiempo_fin_segmento,
                    # Las métricas finales se añadirán después
=======
                    'cpu_original': proceso_actual_ejecutando['duracion_original_calc'],
                    'comienzo': tiempo_inicio_segmento,
                    'final': tiempo_fin_segmento,
>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
                })

                if proceso_actual_ejecutando['restante'] <= 0:
                    procesos_completados_count += 1
<<<<<<< HEAD
                    proceso_actual_ejecutando['tiempo_finalizacion'] = tiempo_actual
                    
                    turnaround = proceso_actual_ejecutando['tiempo_finalizacion'] - proceso_actual_ejecutando['llegada']
                    espera = turnaround - proceso_actual_ejecutando['duracion_original']
                    
                    proceso_actual_ejecutando['turnaround_final'] = turnaround
                    proceso_actual_ejecutando['tiempo_espera_final'] = espera

                    # Guardar stats finales para referencia posterior
                    stats_finales_procesos[proceso_actual_ejecutando['id']] = {
                        'espera': espera,
                        'turnaround': turnaround
                    }
            # Si tiempo_ejecucion_este_slot es 0, tiempo_actual no avanza por ejecución.
            # El bucle se repite, y la selección de procesos_listos_para_ejecutar
            # considerará cualquier proceso que haya llegado exactamente en tiempo_actual.

        # Fin del bucle while

        # Actualizar todos los segmentos con las métricas finales calculadas
        for segmento in lista_segmentos_ejecucion:
            id_proceso_segmento = segmento['proceso']
            if id_proceso_segmento in stats_finales_procesos and stats_finales_procesos[id_proceso_segmento]:
                segmento['espera_final'] = stats_finales_procesos[id_proceso_segmento].get('espera', "Error E")
                segmento['turnaround_final'] = stats_finales_procesos[id_proceso_segmento].get('turnaround', "Error T")
            else:
                # Intentar encontrar el proceso en la lista 'procesos' si no está en stats (debería estar)
                proceso_obj = next((p for p in procesos if p['id'] == id_proceso_segmento), None)
                if proceso_obj and proceso_obj['restante'] <= 0 : # Si terminó
                    segmento['espera_final'] = proceso_obj['tiempo_espera_final']
                    segmento['turnaround_final'] = proceso_obj['turnaround_final']
                else: # Proceso no encontrado o no terminado (no debería pasar si la lógica es correcta)
                    segmento['espera_final'] = "No Term."
                    segmento['turnaround_final'] = "No Term."
        
        return lista_segmentos_ejecucion
=======
                    proceso_actual_ejecutando['tiempo_finalizacion_calc'] = tiempo_actual
                    turnaround = proceso_actual_ejecutando['tiempo_finalizacion_calc'] - proceso_actual_ejecutando['llegada']
                    espera = turnaround - proceso_actual_ejecutando['duracion_original_calc']
                    
                    proceso_actual_ejecutando['turnaround_final_calc'] = turnaround
                    proceso_actual_ejecutando['tiempo_espera_final_calc'] = espera
                    stats_finales_procesos[proceso_actual_ejecutando['id']] = {'espera': espera, 'turnaround': turnaround}

        for segment in lista_segmentos_ejecucion:
            id_proceso_segmento = segment['proceso']
            if id_proceso_segmento in stats_finales_procesos and stats_finales_procesos[id_proceso_segmento]:
                segment['espera_final'] = stats_finales_procesos[id_proceso_segmento].get('espera', 'Error E')
                segment['turnaround_final'] = stats_finales_procesos[id_proceso_segmento].get('turnaround', 'Error T')
            else:
                proceso_obj = next((p for p in procesos if p['id'] == id_proceso_segmento), None)
                if proceso_obj and proceso_obj['restante'] <= 0 :
                    segment['espera_final'] = proceso_obj.get('tiempo_espera_final_calc', 'No Term. (obj)')
                    segment['turnaround_final'] = proceso_obj.get('turnaround_final_calc', 'No Term. (obj)')
                else:
                    segment['espera_final'] = "No Term."
                    segment['turnaround_final'] = "No Term."
        
        return lista_segmentos_ejecucion
    

class MockSRTFController:
    @staticmethod
    def simular_srtf(procesos_iniciales):
        # Reutiliza la lógica de SRTFController
        print("ADVERTENCIA: Usando MockSRTFController que llama a SRTFController. Asegúrate que SRTFController esté implementado.")
        return SRTFController.simular_srtf(procesos_iniciales)
>>>>>>> 2ce6b94a9b4848c25fe812224a6a8c7c74b396f1
