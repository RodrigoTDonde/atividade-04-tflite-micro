# Relatório breve — Hello World com TensorFlow Lite Micro

## Objetivo

O objetivo foi reproduzir o exemplo Hello World do TensorFlow Lite Micro no ESP32-S3, usando ESP-IDF dentro do VS Code e simulando a execução no Wokwi. O programa recebe valores de entrada e estima o seno de cada valor.

## Como o modelo foi usado

O notebook fornecido cria exemplos com `x` entre 0 e `2π` e usa `sin(x)` como resposta esperada. Depois do treinamento, o modelo é convertido para TensorFlow Lite e transformado em um vetor C. Esse vetor está no arquivo `main/model.cc`, permitindo que o ESP32-S3 use o modelo sem sistema de arquivos.

No microcontrolador, o TensorFlow Lite Micro não treina o modelo. Ele apenas faz a inferência com um modelo já treinado, usando memória estática.

## Leitura do código

- `main.cc` chama `setup()` uma vez e `loop()` a cada 500 ms.
- `setup()` abre o modelo, verifica a versão do formato, registra a operação `FullyConnected`, cria o interpretador e reserva a arena de memória dos tensores.
- `loop()` calcula um novo `x`, converte esse valor para o formato inteiro quantizado, executa `Invoke()` e converte a saída novamente para ponto flutuante.
- `output_handler.cc` imprime `x_value` e `y_value` no terminal do Wokwi.

## Observações da simulação

O terminal apresentou valores coerentes com uma senoide. Por exemplo, a saída ficou próxima de `+1` quando `x` chegou perto de `1,57` (π/2), próxima de zero em `3,14` (π) e negativa depois desse ponto. Pequenas diferenças em relação ao seno matemático são esperadas porque o modelo usa quantização int8.

Durante a configuração, a saída ficou constante quando as otimizações ESP-NN estavam ativadas. Essas otimizações usam instruções específicas do ESP32-S3 que o Wokwi não reproduz completamente. O projeto desativa a macro `ESP_NN` no seu próprio CMake, mantendo a alteração reproduzível e sem modificar os arquivos da biblioteca baixada.

## Conclusão

O ESP32-S3 executou o modelo TensorFlow Lite Micro no Wokwi e imprimiu previsões variáveis e coerentes no monitor serial. A imagem `evidencias/01-wokwi-hello-world.png` registra o circuito e as previsões finais.

## Ponto extra — DHT22 e novo dataset

Como extensão, foi criada uma segunda aplicação com um DHT22. Ela lê temperatura e umidade no GPIO 17 e usa um modelo novo para classificar o ambiente como `CONFORTAVEL` ou `ATENCAO`.

O novo dataset tem 1.200 amostras sintéticas e reproduzíveis: 600 situações de conforto e 600 situações fora da faixa. A regra usada nos rótulos foi 20–26 °C e 40–65% de umidade para `CONFORTAVEL`. O modelo foi treinado no Google Colab, convertido para TensorFlow Lite int8 e alcançou 92,5% de acurácia em 240 amostras de teste.

No Wokwi, 24 °C e 50% resultaram em probabilidade 0,98 e classe `CONFORTAVEL`; 32 °C e 70,5% resultaram em probabilidade 0,02 e classe `ATENCAO`. As imagens estão em `extra_dht22/evidencias/`.
