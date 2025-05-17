class RRController:

    @staticmethod
    def simular_rr(procesos, quantum):
        tiempo_actual = 0
        cola = []
        procesos_ordenados = sorted(procesos, key=lambda p: p['llegada'])
        completados = []
        en_cola = set()

        for p in procesos_ordenados:
            p['restante'] = p['duracion']
            p['comienzo'] = -1

        while procesos_ordenados or cola:
            # Ingresar procesos que han llegado
            while procesos_ordenados and procesos_ordenados[0]['llegada'] <= tiempo_actual:
                p = procesos_ordenados.pop(0)
                cola.append(p)
                en_cola.add(p['nombre'])

            if not cola:
                tiempo_actual += 1
                continue

            actual = cola.pop(0)

            if actual['comienzo'] == -1:
                actual['comienzo'] = tiempo_actual

            ejecutar = min(quantum, actual['restante'])
            tiempo_actual += ejecutar
            actual['restante'] -= ejecutar

            # Verificar nuevos que llegan durante ejecución
            while procesos_ordenados and procesos_ordenados[0]['llegada'] <= tiempo_actual:
                p = procesos_ordenados.pop(0)
                cola.append(p)
                en_cola.add(p['nombre'])

            if actual['restante'] > 0:
                cola.append(actual)
            else:
                actual['final'] = tiempo_actual
                actual['espera'] = actual['final'] - actual['llegada'] - actual['duracion']
                actual['turnaround'] = actual['final'] - actual['llegada']
                completados.append(actual)

        # Convertir claves a minúsculas para que concuerden con el frontend
        resultado_final = []
        for p in completados:
            resultado_final.append({
                'proceso': p['nombre'],
                'llegada': p['llegada'],
                'cpu': p['duracion'],
                'comienzo': p['comienzo'],
                'final': p['final'],
                'espera': p['espera'],
                'turnaround': p['turnaround']
            })

        return resultado_final