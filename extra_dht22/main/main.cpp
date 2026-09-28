#include <cmath>

#include <dht.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_log.h"
#include "tensorflow/lite/schema/schema_generated.h"

extern const unsigned char g_model_dht22[];
extern const int g_model_dht22_len;

namespace {
constexpr gpio_num_t DHT_GPIO = GPIO_NUM_17;
constexpr size_t TENSOR_ARENA_SIZE = 12 * 1024;
constexpr float LIMIAR_CONFORTO = 0.5f;
constexpr char TAG[] = "DHT22_TFLITE";

uint8_t tensor_arena[TENSOR_ARENA_SIZE];
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

int8_t quantizar(float valor, const TfLiteTensor* tensor) {
  const float quantizado = valor / tensor->params.scale + tensor->params.zero_point;
  return static_cast<int8_t>(fmaxf(-128.0f, fminf(127.0f, roundf(quantizado))));
}

float desquantizar(int8_t valor, const TfLiteTensor* tensor) {
  return (valor - tensor->params.zero_point) * tensor->params.scale;
}

bool iniciar_modelo() {
  const tflite::Model* model = tflite::GetModel(g_model_dht22);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    ESP_LOGE(TAG, "Schema do modelo incompatível");
    return false;
  }

  static tflite::MicroMutableOpResolver<2> resolver;
  if (resolver.AddFullyConnected() != kTfLiteOk || resolver.AddLogistic() != kTfLiteOk) {
    ESP_LOGE(TAG, "Não foi possível registrar as operações do modelo");
    return false;
  }

  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, TENSOR_ARENA_SIZE);
  interpreter = &static_interpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk) {
    ESP_LOGE(TAG, "Falha ao reservar os tensores");
    return false;
  }

  input = interpreter->input(0);
  output = interpreter->output(0);
  if (input->type != kTfLiteInt8 || output->type != kTfLiteInt8 || input->bytes != 2) {
    ESP_LOGE(TAG, "Formato de tensor inesperado");
    return false;
  }
  return true;
}
}  // namespace

extern "C" void app_main(void) {
  ESP_LOGI(TAG, "Ponto extra: DHT22 + modelo TensorFlow Lite Micro");
  ESP_LOGI(TAG, "DHT22: DATA=GPIO 17 | conforto: 20-26 C e 40-65 %%");

  if (!iniciar_modelo()) {
    ESP_LOGE(TAG, "Aplicação interrompida: modelo inválido");
    return;
  }
  ESP_LOGI(TAG, "Modelo int8 inicializado (%d bytes)", g_model_dht22_len);

  while (true) {
    float umidade = NAN;
    float temperatura = NAN;
    const esp_err_t erro = dht_read_float_data(DHT_TYPE_AM2301, DHT_GPIO,
                                                 &umidade, &temperatura);
    if (erro != ESP_OK) {
      ESP_LOGW(TAG, "Falha ao ler DHT22: %s", esp_err_to_name(erro));
      vTaskDelay(pdMS_TO_TICKS(2000));
      continue;
    }

    input->data.int8[0] = quantizar(temperatura, input);
    input->data.int8[1] = quantizar(umidade, input);
    if (interpreter->Invoke() != kTfLiteOk) {
      ESP_LOGE(TAG, "Falha durante a inferência");
      vTaskDelay(pdMS_TO_TICKS(2000));
      continue;
    }

    const float probabilidade = desquantizar(output->data.int8[0], output);
    const char* classe = probabilidade >= LIMIAR_CONFORTO ? "CONFORTAVEL" : "ATENCAO";
    ESP_LOGI(TAG, "Temp=%.1f C | Umidade=%.1f %% | Prob=%.2f | Classe=%s",
             static_cast<double>(temperatura), static_cast<double>(umidade),
             static_cast<double>(probabilidade), classe);
    vTaskDelay(pdMS_TO_TICKS(2000));
  }
}
