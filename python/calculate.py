# Librerias
import glob
import pandas as pd
import numpy as np

def calculoImpuesto(batch: list, impuesto_acumulado_previo: float = 0, num_filas_previo: int = 0) -> tuple:
    """
    Calcula el impuesto al consumo para un batch de datos, teniendo en cuenta valores acumulados previos.
    
    Args:
        batch (list): Lista de diccionarios con los datos a procesar
        num_filas_previo (int): Número de filas procesadas previamente
        impuesto_acumulado_previo (float): Impuesto acumulado de procesamiento previo
        
    Returns:
        tuple: (lista_procesada, impuesto_acumulado_total, num_filas_total)
    """

    # Calculo de la tasa de impuestos al consumo
    df_consolidado = pd.DataFrame(batch)
    # Diccionarios base
    minimos = {2023: 2353.25, 2024: 2120.60}
    maximos = {
        2023: {'Industrial': 1804206.48, 'Comercial': 1484420},
        2024: {'Industrial': 2002145.10, 'Comercial': 1647275.00}
    }
    tarifa_dif_residencial = {
        'Comercial': 0.017, 'Industrial': 0.017,
        'Oficial': 0.01, 'Especial': 0.017, 'Otros': 0.017
    }
    tarifa_residencial = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0.01, 5: 0.02, 6: 0.02}
    # Crear columnas auxiliares para minimo y maximo por anio
    df_copy = df_consolidado.copy()
    df_copy['minimo'] = df_copy['anio'].map(minimos)
    # Mapear el valor máximo por anio y destino
    df_copy['maximo'] = df_copy.apply(lambda row: maximos[row['anio']].get(row['destino'], np.inf), axis=1)
    # 1. porque usa el np.inf
    # Crear columna 'tarifa' para no-residenciales
    df_copy['tarifa'] = df_copy['destino'].map(tarifa_dif_residencial)
    # Para residenciales, asignamos tarifa por estrato (donde tarifa está vacía)
    mask_residencial = df_copy['tarifa'].isna()
    df_copy.loc[mask_residencial, 'tarifa'] = df_copy.loc[mask_residencial, 'estrato'].map(tarifa_residencial)

    # Calcular Impuesto
    # Condición: consumo mayor o igual al mínimo
    cond_consumo_valido = df_copy['consumo'] >= df_copy['minimo']

    # Cálculo del impuesto
    df_copy['impuesto_al_consumo'] = np.where(
        cond_consumo_valido,
        df_copy['consumo'] * df_copy['tarifa'],
        0
    )

    df_consolidado['impuesto_al_consumo'] = df_copy['impuesto_al_consumo']    
    
    ## Calcular el impuesto acumulado para cada fila, partiendo del impuesto_acumulado_previo
    df_consolidado['impuesto_acumulado_sum'] = df_consolidado['impuesto_al_consumo'].cumsum() + impuesto_acumulado_previo
    
    # Obtener el impuesto total acumulado (último valor + previo)
    impuesto_acumulado_total = impuesto_acumulado_previo
    if not df_consolidado.empty:
        impuesto_acumulado_total = df_consolidado['impuesto_acumulado_sum'].iloc[-1]

    impuesto_acumulado_total = impuesto_acumulado_total.item()  
    
    # Número de filas total (previo + actual)
    num_filas_total = num_filas_previo + len(df_consolidado)

    # Añadir información sobre la numeración de filas
    df_consolidado['num_fila'] = range(num_filas_previo + 1, num_filas_total + 1)
    
    # Convertir a lista de diccionarios
    lista_dicts = df_consolidado.to_dict(orient="records")

    # Devolver la lista de diccionarios, el impuesto acumulado total y el número de filas total
    return lista_dicts, impuesto_acumulado_total, num_filas_total
