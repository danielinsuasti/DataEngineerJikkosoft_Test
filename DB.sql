  CREATE SCHEMA pipeline;

  -- Creación de la tabla consumo
  --DROP TABLE pipeline.consumo;
  CREATE TABLE pipeline.consumo ( 
    id VARCHAR(50) NOT NULL,
    anio INTEGER NOT NULL, 
    destino VARCHAR(50),
    estrato VARCHAR(50),
    consumo NUMERIC(12,2) NOT NULL,
    impuesto_al_consumo NUMERIC(15,2) NOT NULL,
    impuesto_acumulado_sum NUMERIC(15,2) NOT NULL,
    PRIMARY KEY ( id, anio ) 
  );

  -- Creación de la tabla log_consumo_calculado
  --DROP TABLE pipeline.log_consumo_calculado;
CREATE TABLE pipeline.log_consumo_calculado (
    id serial,     
    cantidad_cargada INTEGER NOT NULL, 
    impuesto_acumulado_sum NUMERIC(15,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   
    PRIMARY KEY ( id ) 
  );

  -- Creación de la tabla consumo_maximo
  --DROP TABLE pipeline.consumo_maximo;
  CREATE TABLE pipeline.consumo_maximo ( 
    anio INTEGER NOT NULL, 
    destino VARCHAR(50) NOT NULL,
    maximo NUMERIC(12,2) NOT NULL,  
    PRIMARY KEY ( anio, destino ) 
  );

  -- Sentencias INSERT para la tabla consumo_maximo
  INSERT INTO pipeline.consumo_maximo (anio, destino, maximo) VALUES
  (2024, 'Industrial', 2002145.10),
  (2024, 'Comercial', 1647275.00),
  (2023, 'Industrial', 1804206.48),
  (2023, 'Comercial', 1484420.00);

  -- Creación de la tabla consumo_minimo
  --DROP TABLE pipeline.consumo_minimo;
  CREATE TABLE pipeline.consumo_minimo ( 
    anio INTEGER NOT NULL,   
    minimo NUMERIC(12,2) NOT NULL,  
    PRIMARY KEY ( anio ) 
  );

  -- Sentencias INSERT para la tabla consumo_minimo
  INSERT INTO pipeline.consumo_minimo (anio, minimo) VALUES
  (2024, 2353.25),
  (2023, 2120.60);


  -- Creación de la tabla tarifas_destino
  --DROP TABLE pipeline.tarifas_destino;
  CREATE TABLE pipeline.tarifas_destino ( 
    id serial,
    destino VARCHAR(50) NOT NULL,
    estrato VARCHAR(50),
    tarifa_porcentaje NUMERIC(5,3) NOT NULL,  
    PRIMARY KEY ( id ) 
  );

  -- Sentencias INSERT para la tabla tarifas_destino
  INSERT INTO pipeline.tarifas_destino (destino, estrato, tarifa_porcentaje) VALUES
  ('Comercial', NULL, 0.017),
  ('Industrial', NULL, 0.017),
  ('Oficial', NULL, 0.010),
  ('Especial', NULL, 0.017),
  ('Otros', NULL, 0.017),
  ('Residencial', 0, 0.0),
  ('Residencial', 1, 0.0),
  ('Residencial', 2, 0.0),
  ('Residencial', 3, 0.0),
  ('Residencial', 4, 0.010),
  ('Residencial', 5, 0.020),
  ('Residencial', 6, 0.020);