batch_counter = 0
batch_size = 1000
processed_files = {}

function process(tag, timestamp, record)
    -- Manejar primera línea de cada archivo si tienes Path_Key configurado
    local path = record["file_path"] or ""
    if path ~= "" and not processed_files[path] then
        processed_files[path] = true
        return -1, 0, 0  -- Ignorar esta primera línea
    end
    
    -- Tratar específicamente el campo estrato
    if not record["estrato"] or record["estrato"] == "" then
        record["estrato"] = "-1"
    end

    -- Lógica de procesamiento por lotes
    batch_counter = batch_counter + 1
    
    if batch_counter <= batch_size then
        return 1, timestamp, record
    else
        -- Pausar brevemente después de cada lote
        os.execute("sleep 2.0")
        batch_counter = 1
        return 1, timestamp, record
    end
end