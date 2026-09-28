# Atividade 4 — Hello World com TensorFlow Lite Micro

Aplicação embarcada executada no **ESP32-S3 DevKitC-1** pelo Wokwi, usando ESP-IDF e TensorFlow Lite Micro. O modelo aproxima a função seno: recebe um valor `x` entre 0 e `2π` e imprime a previsão `y` no monitor serial.

## Resultado

A simulação foi validada no Wokwi. A evidência está em [evidencias/01-wokwi-hello-world.png](evidencias/01-wokwi-hello-world.png).

Exemplos observados no terminal:

```text
x_value: 0.000000, y_value: 0.000000
x_value: 1.570796, y_value: 1.042060
x_value: 3.141593, y_value: 0.008472
x_value: 4.712389, y_value: -1.109837
```

Os valores são aproximações do seno e podem passar um pouco de `+1` ou `-1` por causa da quantização do modelo.

## Como executar

1. Abra esta pasta no VS Code com as extensões **Espressif IDF** e **Wokwi** instaladas.
2. Ative o ambiente ESP-IDF e execute `idf.py build` com alvo `esp32s3`.
3. Pressione `F1`, execute `Wokwi: Start Simulator` e acompanhe o **Wokwi Terminal**.

O arquivo `wokwi.toml` aponta o simulador para o firmware gerado em `build/` e `diagram.json` define a placa ESP32-S3 e a conexão com o monitor serial.

## Arquivos principais

| Arquivo | Finalidade |
| --- | --- |
| `main/main.cc` | Inicia a aplicação e executa uma inferência a cada 500 ms. |
| `main/main_functions.cc` | Prepara o interpretador TFLite Micro, processa a entrada e executa a inferência. |
| `main/model.cc` | Modelo TensorFlow Lite convertido para um vetor C. |
| `main/output_handler.cc` | Imprime `x_value` e `y_value` no terminal. |
| `RELATORIO.md` | Análise breve da atividade. |

## Compatibilidade com o Wokwi

O componente `espressif/esp-tflite-micro` está fixado na versão `1.4.0`. Em `main/CMakeLists.txt`, a macro `ESP_NN` é removida somente para esse componente. Isso evita que as otimizações em assembly do ESP32-S3, que não são reproduzidas pelo Wokwi, alterem a saída do modelo.
