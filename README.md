# Atividade Avaliativa Prática 4/6 — TensorFlow Lite Micro

Este repositório documenta uma aplicação embarcada desenvolvida com **ESP-IDF**, **C/C++**, **TensorFlow Lite Micro** e o simulador **Wokwi**, tendo como alvo o **ESP32-S3 DevKitC-1**. O trabalho contém a reprodução do exemplo Hello World e uma extensão autoral com sensor DHT22, realizada para o ponto extra da atividade.

## Objetivos atendidos

- reproduzir o exemplo Hello World do TensorFlow Lite Micro no ESP32-S3;
- executar a simulação no Wokwi e observar as inferências no monitor serial;
- documentar a análise do código e os resultados obtidos;
- desenvolver, como ponto extra, uma nova aplicação com sensor, dataset e modelo treinado especificamente para a nova funcionalidade.

## Parte 1 — Hello World

O exemplo Hello World utiliza um modelo que aproxima a função seno. A cada 500 ms, a aplicação fornece um valor `x` ao modelo e imprime no terminal a previsão `y` correspondente. O modelo TensorFlow Lite já treinado é incorporado ao firmware como um vetor C; portanto, o microcontrolador executa somente a inferência.

Durante a simulação, foram observados os seguintes valores:

```text
x_value: 0.000000, y_value: 0.000000
x_value: 1.570796, y_value: 1.042060
x_value: 3.141593, y_value: 0.008472
x_value: 4.712389, y_value: -1.109837
```

Os resultados acompanham o comportamento esperado de uma senoide. Pequenas diferenças em relação ao valor matemático exato são esperadas, pois o modelo usa quantização int8.

**Evidência:** [evidencias/01-wokwi-hello-world.png](evidencias/01-wokwi-hello-world.png).

## Parte 2 — Ponto extra: classificador ambiental com DHT22

A pasta [extra_dht22](extra_dht22/) contém uma aplicação independente que lê temperatura e umidade de um DHT22 conectado ao GPIO 17. Um modelo TensorFlow Lite Micro classifica o ambiente em duas categorias:

| Classe | Critério utilizado |
| --- | --- |
| `CONFORTAVEL` | Temperatura entre 20 e 26 °C e umidade entre 40 e 65%. |
| `ATENCAO` | Qualquer condição fora dessa faixa. |

O modelo foi treinado no Google Colab com um novo dataset sintético e reproduzível de 1.200 amostras, dividido em 960 amostras de treino e 240 de teste. A acurácia registrada no conjunto de teste foi **92,5%**. O script de treinamento, o dataset, as métricas e o modelo convertido estão versionados para permitir a verificação do procedimento.

As evidências mostram a classificação `CONFORTAVEL` para 24 °C e 50% de umidade e `ATENCAO` para 32 °C e 70,5% de umidade. Consulte a documentação específica em [extra_dht22/README.md](extra_dht22/README.md).

## Organização do repositório

| Caminho | Conteúdo |
| --- | --- |
| `main/` | Código-fonte do Hello World e modelo incorporado ao firmware. |
| `evidencias/` | Captura da simulação do Hello World no Wokwi. |
| `RELATORIO.md` | Relatório breve com análise do código e observações. |
| `extra_dht22/` | Aplicação do ponto extra, incluindo código, circuito, treinamento, dataset, modelo e evidências. |
| `diagram.json` e `wokwi.toml` | Definição do circuito e configuração da simulação do Hello World. |

## Como reproduzir a Parte 1

1. Abra esta pasta no VS Code com as extensões **Espressif IDF** e **Wokwi** instaladas.
2. Configure o alvo `esp32s3` e execute `idf.py build` no terminal ESP-IDF.
3. Pressione `F1`, selecione `Wokwi: Start Simulator` e acompanhe o **Wokwi Terminal**.

O arquivo `wokwi.toml` aponta para o firmware produzido em `build/`, enquanto `diagram.json` descreve a placa ESP32-S3 e o monitor serial.

## Aspecto de compatibilidade da simulação

O componente `espressif/esp-tflite-micro` está fixado na versão `1.4.0`. O arquivo `main/CMakeLists.txt` desativa a macro `ESP_NN` somente para esse componente. Essa configuração evita que otimizações em assembly específicas do ESP32-S3, não reproduzidas integralmente pelo Wokwi, alterem o resultado da inferência na simulação.

## Documentação complementar

- [Relatório breve](RELATORIO.md)
- [Documentação do ponto extra](extra_dht22/README.md)
