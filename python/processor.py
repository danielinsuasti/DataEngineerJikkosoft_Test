import json
import logging 
from kafka import KafkaConsumer
import psycopg2
import time

import calculate

# Configuración básica para mostrar logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('app.log')]
)

# Configuración del lote
BATCH_SIZE = 1000
BATCH_TIMEOUT = 10  # segundos
impuesto_acumulado = 0
num_filas = 0

def grabar_log(cantidad_cargada, impuesto_acumulado):
    # Aquí puedes implementar la lógica para grabar el log en la base de datos    
    sql = "INSERT INTO pipeline.log_consumo_calculado (cantidad_cargada, impuesto_acumulado_sum) VALUES (%s,%s)"
    
    try:
        cur.execute( 
            sql, 
            (cantidad_cargada, impuesto_acumulado) 
        ) 
        conn.commit()          
        logging.info(f"Cantidad cargada: {cantidad_cargada}, Impuesto acumulado: {impuesto_acumulado}:")
        
    except Exception as e:
        logging.error(f"ERROR: Fallo en inserción del LOG: {e}")
        conn.rollback()
        return 0



def process_batch(batch_in):
    global impuesto_acumulado
    global num_filas
    #logging.info( "{0}".format( batch_in ) )
    batch, impuesto_acumulado, num_filas = calculate.calculoImpuesto(batch_in, impuesto_acumulado, num_filas)        
    grabar_log(len(batch), impuesto_acumulado)
    
    """ 
    if impuesto_acumulado == 0 and num_filas == 0:
        batch, impuesto_acumulado, num_filas = calculate.calculoImpuesto(batch_in, impuesto_acumulado, num_filas)        
        grabar_log(len(batch), impuesto_acumulado)
    else:
        batch, impuesto_acumulado, num_filas = calculate.calculoImpuesto(batch_in, impuesto_acumulado, num_filas)        
        grabar_log(len(batch), impuesto_acumulado)
    """
           

    #batch = calculate.calculoImpuesto(batch_in, impuesto_acumulado_in = impuesto_acumulado, num_filas_in = num_filas)
    """Procesa un lote de registros"""
    if not batch:
        return 0
    
    sql = "INSERT INTO pipeline.consumo (id, anio, destino, estrato, consumo, impuesto_al_consumo, impuesto_acumulado_sum) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    try:
        values = [(r["id"], r["anio"], r["destino"], r["estrato"], r["consumo"], r["impuesto_al_consumo"], r["impuesto_acumulado_sum"]) for r in batch]
        cur.executemany(sql, values)
        conn.commit()
        logging.info(f"ÉXITO: Procesados {len(batch)} registros")
        return len(batch)
    except Exception as e:
        logging.error(f"ERROR: Fallo en inserción: {e}")
        conn.rollback()
        return 0

# Conexión a la base de datos
conn = psycopg2.connect(
    database="postgresdb", host="127.0.0.1", 
    user="postgres", password="postgres", port="5432"
) 
cur = conn.cursor()

# Configuración del consumidor de Kafka
consumer = KafkaConsumer( 
    'pipeline',  # Tópico directamente especificado
    group_id='my-group', 
    bootstrap_servers=['127.0.0.1:29092'], 
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    enable_auto_commit=False,
    auto_offset_reset='earliest'
)

try:
    batch = []
    last_batch_time = time.time()
    total_processed = 0
    
    while True:
        # Procesar lote completo si ya tenemos suficientes mensajes
        if len(batch) >= BATCH_SIZE:
            process_batch_size = BATCH_SIZE
            total_processed += process_batch(batch[:process_batch_size])
            batch = batch[process_batch_size:]
            consumer.commit()
            last_batch_time = time.time()
            continue
        
        # Verificar timeout para lotes parciales
        if batch and time.time() - last_batch_time > BATCH_TIMEOUT:
            total_processed += process_batch(batch)
            batch = []
            consumer.commit()
            last_batch_time = time.time()
            continue
        
        # Obtener más mensajes
        messages = consumer.poll(timeout_ms=100)
        if not messages:
            time.sleep(0.1)
            continue
            
        # Procesar mensajes recibidos
        for tp, msgs in messages.items():
            for msg in msgs:
                if isinstance(msg.value, dict) and all(k in msg.value for k in ["id", "anio", "destino", "estrato", "consumo"]):
                    batch.append({
                        "id": msg.value["id"],
                        "anio": int(msg.value["anio"]),
                        "destino": msg.value["destino"],
                        "estrato": int(msg.value["estrato"]),
                        "consumo": float(msg.value["consumo"])
                    })
                else:
                    logging.warning(f"Mensaje con formato incorrecto: {msg.value}")

except KeyboardInterrupt:
    logging.info("Interrupción de usuario detectada")
    
    # Procesar mensajes restantes
    while batch:
        process_size = min(len(batch), BATCH_SIZE)
        total_processed += process_batch(batch[:process_size])
        batch = batch[process_size:]
        consumer.commit()
    
    logging.info(f"Total procesado: {total_processed} mensajes")

except Exception as e:
    logging.error(f"Error inesperado: {e}")
    import traceback
    logging.error(traceback.format_exc())

finally:
    consumer.close()
    cur.close()
    conn.close()
    logging.info("Consumidor finalizado correctamente")