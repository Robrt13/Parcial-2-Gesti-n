def calcular_alerta(criticidad: int, sentimiento: float) -> tuple[bool, int]:
    ALERTAS = {
        True: {
            4: 0,
            5: 1,
            6: 2,
            7: 3
        },
        False: {
            4: 0,
            5: 0,
            6: 1,
            7: 2
        }
    }
    
    if criticidad <= 4:
        rango_criticidad = 4
    elif criticidad >= 7:
        rango_criticidad = 7
    else:
        rango_criticidad = criticidad
    sentimiento_negativo = sentimiento < 0.0
    nivel_alerta = ALERTAS[sentimiento_negativo][rango_criticidad]
    return nivel_alerta != 0, nivel_alerta