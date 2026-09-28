# Ponto extra — Classificador com DHT22

Esta aplicação é independente do Hello World. Ela lê temperatura e umidade de um DHT22 e usa um modelo TensorFlow Lite Micro treinado para classificar a condição do ambiente:

- `CONFORTAVEL`: 20 a 26 °C e 40 a 65 % de umidade;
- `ATENCAO`: qualquer leitura fora dessa faixa.

O dataset é sintético e reproduzível. Ele contém 1.200 combinações de temperatura (15 a 35 °C) e umidade (25 a 85 %), geradas com semente fixa. A regra de classificação é registrada no script de treinamento para deixar claro como os rótulos foram definidos.

## Treinamento

Abra o Google Colab, crie um notebook novo, copie o conteúdo de `training/treinar_dht22.py` para uma célula e execute-a. Depois baixe a pasta `artefatos_dht22` como ZIP. Ela conterá `model_data.cc`, o dataset e as métricas que serão usados na aplicação ESP-IDF.

## Resultado do treinamento

O modelo foi treinado no Google Colab com 960 amostras de treino e 240 de teste. A acurácia obtida no conjunto de teste foi **92,5%**. Os arquivos gerados estão em `artefatos/artefatos_dht22/`:

- `dataset_dht22.csv`: dataset usado no treinamento;
- `modelo_dht22_int8.tflite`: modelo quantizado;
- `model_data.cc`: modelo convertido para código C++ do ESP32-S3;
- `metricas.txt`: quantidade de amostras, acurácia e perda.

## Circuito e execução

O DHT22 é alimentado por 3,3 V, ligado ao GND e tem seu pino de dados conectado ao GPIO 17. Um resistor de 10 kΩ faz o pull-up entre 3,3 V e o pino de dados. A leitura ocorre a cada dois segundos e o terminal mostra temperatura, umidade, probabilidade e classe.

As evidências do Wokwi mostram os dois comportamentos esperados:

- [01-confortavel.png](evidencias/01-confortavel.png): 24 °C e 50%, com probabilidade 0,98 e classe `CONFORTAVEL`;
- [02-atencao.png](evidencias/02-atencao.png): 32 °C e 70,5%, com probabilidade 0,02 e classe `ATENCAO`.
