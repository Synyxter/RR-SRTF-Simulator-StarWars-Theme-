import heapq # Para SRTF, si se usa un heap para la cola de listos (opcional)

class RRController:
    """
    Controlador para simular el algoritmo de planificación Round Robin (RR).
    Este es el código que proporcionaste.
    Nota: La salida de este controlador debe ser compatible con lo que espera
    ResultsView para generar la tabla y el diagrama de Gantt.
    Específicamente, la lista de resultados debe contener diccionarios con claves como:
    'proceso', 'llegada', 'cpu' (ráfaga original), 'comienzo', 'final', 'espera', 'turnaround'.
    El código original de ResultsView espera 'cpu_total' para la ráfaga original y
    'comienzos_segmento'/'fines_segmento' si un proceso tiene múltiples segmentos.
    Este controlador parece generar un resultado final por proceso, no por segmento.
    Para un Gantt detallado, se necesitarían los segmentos de ejecución individuales.
    Ajustaré la salida para que sea una lista de segmentos, similar a MockRRController.
    """
    @staticmethod
    def simular_rr(procesos_iniciales, quantum):
        results_list_of_segments = []
        if not procesos_iniciales:
            return []

        # Copiar procesos para no modificar la lista original y añadir campos necesarios
        procesos_para_simular = []
        for p_orig in procesos_iniciales:
            p_copy = p_orig.copy() # nombre, llegada, duracion (o duracion_original)
            # Asegurar que la clave de duración sea consistente, ej. 'duracion_original'
            duracion_key = 'duracion_original' if 'duracion_original' in p_copy else 'duracion'
            if duracion_key not in p_copy:
                 print(f"ADVERTENCIA (RRController): Proceso {p_copy.get('nombre')} no tiene clave de duración ('duracion' o 'duracion_original'). Asumiendo 1.")
                 p_copy[duracion_key] = 1

            p_copy['restante'] = p_copy[duracion_key]
            p_copy['duracion_original_calc'] = p_copy[duracion_key] # Guardar para cálculo final
            p_copy['tiempo_finalizacion_calc'] = 0
            p_copy['tiempo_espera_final_calc'] = "Calc..."
            p_copy['turnaround_final_calc'] = "Calc..."
            # p_copy['primer_comienzo_ejecucion'] = -1 # No usado directamente en esta versión de salida por segmento
            procesos_para_simular.append(p_copy)

        procesos_para_simular.sort(key=lambda p: p['llegada'])

        tiempo_actual = 0
        cola_listos = []
        idx_proceso_entrante = 0
        procesos_terminados_count = 0

        # Diccionario para almacenar las estadísticas finales calculadas para cada proceso
        stats_finales_procesos = {p['nombre']: {} for p in procesos_para_simular}


        while procesos_terminados_count < len(procesos_para_simular):
            # Añadir procesos que han llegado a la cola de listos
            while idx_proceso_entrante < len(procesos_para_simular) and \
                  procesos_para_simular[idx_proceso_entrante]['llegada'] <= tiempo_actual:
                proceso_a_encolar = procesos_para_simular[idx_proceso_entrante]
                if proceso_a_encolar not in cola_listos: # Evitar duplicados si ya está
                    cola_listos.append(proceso_a_encolar)
                idx_proceso_entrante += 1

            if not cola_listos:
                if idx_proceso_entrante < len(procesos_para_simular):
                    tiempo_actual = procesos_para_simular[idx_proceso_entrante]['llegada']
                else: # No hay más procesos por llegar y la cola está vacía
                    break
                continue # Re-evaluar llegadas con el nuevo tiempo_actual

            proceso_actual_ref = cola_listos.pop(0)
            tiempo_inicio_segmento = tiempo_actual

            tiempo_ejecucion_este_quantum = min(proceso_actual_ref['restante'], quantum)
            proceso_actual_ref['restante'] -= tiempo_ejecucion_este_quantum
            tiempo_actual += tiempo_ejecucion_este_quantum
            tiempo_fin_segmento = tiempo_actual

            results_list_of_segments.append({
                'proceso': proceso_actual_ref['nombre'],
                'llegada': proceso_actual_ref['llegada'],
                'cpu_original': proceso_actual_ref['duracion_original_calc'], # Ráfaga total original
                'comienzo': tiempo_inicio_segmento,
                'final': tiempo_fin_segmento,
                'espera_final': "Calc...", # Se actualizará después
                'turnaround_final': "Calc..." # Se actualizará después
            })

            # Volver a añadir procesos que pudieron haber llegado MIENTRAS este se ejecutaba
            # Esto es importante para que no se "salten" llegadas y se coloquen correctamente en la cola.
            nuevos_llegados_durante_ejecucion = []
            while idx_proceso_entrante < len(procesos_para_simular) and \
                  procesos_para_simular[idx_proceso_entrante]['llegada'] <= tiempo_actual:
                proceso_nuevo_llegado = procesos_para_simular[idx_proceso_entrante]
                if proceso_nuevo_llegado not in cola_listos and proceso_nuevo_llegado['restante'] > 0:
                    nuevos_llegados_durante_ejecucion.append(proceso_nuevo_llegado)
                idx_proceso_entrante += 1
            
            # Añadir el proceso actual de nuevo a la cola si aún tiene restante
            if proceso_actual_ref['restante'] > 0:
                cola_listos.append(proceso_actual_ref)
            else: # Proceso terminado
                proceso_actual_ref['tiempo_finalizacion_calc'] = tiempo_actual
                turnaround_final = proceso_actual_ref['tiempo_finalizacion_calc'] - proceso_actual_ref['llegada']
                espera_final = turnaround_final - proceso_actual_ref['duracion_original_calc']

                stats_finales_procesos[proceso_actual_ref['nombre']]['espera'] = espera_final
                stats_finales_procesos[proceso_actual_ref['nombre']]['turnaround'] = turnaround_final
                procesos_terminados_count += 1

            # Añadir los nuevos llegados (después del proceso actual si no ha terminado)
            # para mantener el orden RR (los que llegan se añaden al final de la cola)
            for p_nl in nuevos_llegados_durante_ejecucion:
                 if p_nl not in cola_listos : # Doble chequeo por si acaso
                    cola_listos.append(p_nl)


        # Actualizar 'espera_final' y 'turnaround_final' en todos los segmentos con los valores calculados
        for segment in results_list_of_segments:
            nombre_proceso_segmento = segment['proceso']
            if nombre_proceso_segmento in stats_finales_procesos and stats_finales_procesos[nombre_proceso_segmento]:
                segment['espera_final'] = stats_finales_procesos[nombre_proceso_segmento].get('espera', 'Error E')
                segment['turnaround_final'] = stats_finales_procesos[nombre_proceso_segmento].get('turnaround', 'Error T')
            else: # Si un proceso no terminó (no debería pasar si la lógica es correcta)
                # O si el proceso terminó pero no se encontró en stats_finales_procesos
                proceso_obj = next((p for p in procesos_para_simular if p['nombre'] == nombre_proceso_segmento), None)
                if proceso_obj and proceso_obj['restante'] <= 0: # Si terminó
                    segment['espera_final'] = proceso_obj.get('tiempo_espera_final_calc', 'No Term. (obj)')
                    segment['turnaround_final'] = proceso_obj.get('turnaround_final_calc', 'No Term. (obj)')
                else:
                    segment['espera_final'] = "No Term."
                    segment['turnaround_final'] = "No Term."
        
        return results_list_of_segments
    

class MockRRController:
    @staticmethod
    def simular_rr(procesos_iniciales, quantum):
        # Reutiliza la lógica de RRController o una versión simplificada si es necesario
        # Para este ejemplo, simplemente llamaremos al RRController real.
        # Si RRController no estuviera listo, aquí iría una simulación mock.
        print("ADVERTENCIA: Usando MockRRController que llama a RRController. Asegúrate que RRController esté implementado.")
        return RRController.simular_rr(procesos_iniciales, quantum)