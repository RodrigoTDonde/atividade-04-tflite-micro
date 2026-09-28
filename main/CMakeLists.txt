
#
# Componente principal do exemplo TensorFlow Lite Micro Hello World.
#

idf_component_register(
    SRCS main.cc main_functions.cc constants.cc output_handler.cc model.cc
    PRIV_REQUIRES spi_flash
    INCLUDE_DIRS "")

# O componente esp-tflite-micro 1.4.0 habilita ESP-NN por padrão. O Wokwi não
# emula as instruções de otimização do ESP32-S3; remover a macro faz o modelo
# usar a implementação de referência e preserva resultados corretos no
# simulador. A mudança fica no projeto, sem editar managed_components.
idf_component_get_property(tflite_micro_lib espressif__esp-tflite-micro COMPONENT_LIB)
target_compile_options(${tflite_micro_lib} PRIVATE -UESP_NN)
