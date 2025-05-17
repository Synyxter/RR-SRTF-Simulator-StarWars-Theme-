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

        procesos = []
        for i, p_orig in enumerate(procesos_iniciales):
            p_copy = p_orig.copy()
            p_copy['id'] = p_orig.get('nombre', f"Proceso_{i+1}")
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
            procesos_listos_para_ejecutar = [
                p for p in procesos if p['llegada'] <= tiempo_actual and p['restante'] > 0
            ]

            if not procesos_listos_para_ejecutar:
                tiempos_llegada_futuros = [
                    p['llegada'] for p in procesos if p['llegada'] > tiempo_actual and p['restante'] > 0
                ]
                if not tiempos_llegada_futuros:
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
            
            if tiempo_ejecucion_este_slot > 0:
                proceso_actual_ejecutando['restante'] -= tiempo_ejecucion_este_slot
                tiempo_actual += tiempo_ejecucion_este_slot
                tiempo_fin_segmento = tiempo_actual

                lista_segmentos_ejecucion.append({
                    'proceso': proceso_actual_ejecutando['id'],
                    'llegada': proceso_actual_ejecutando['llegada'],
                    'cpu_original': proceso_actual_ejecutando['duracion_original_calc'],
                    'comienzo': tiempo_inicio_segmento,
                    'final': tiempo_fin_segmento,
                })

                if proceso_actual_ejecutando['restante'] <= 0:
                    procesos_completados_count += 1
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