idf_component_register(
    SRCS "main.cpp" "../artefatos/artefatos_dht22/model_data.cc"
    PRIV_REQUIRES spi_flash
    INCLUDE_DIRS "")

# O Wokwi não reproduz as otimizações ESP-NN em assembly do ESP32-S3.
idf_component_get_property(tflite_micro_lib espressif__esp-tflite-micro COMPONENT_LIB)
target_compile_options(${tflite_micro_lib} PRIVATE -UESP_NN)
