"""Treina o modelo do ponto extra: conforto ambiental com DHT22."""

from pathlib import Path
import csv
import numpy as np
import tensorflow as tf

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)
OUTPUT = Path("artefatos_dht22")
OUTPUT.mkdir(exist_ok=True)

# Dataset novo e sintético, balanceado: 600 casos confortáveis e 600 fora da
# faixa. Conforto exige 20-26 °C e 40-65 % de umidade.
por_classe = 600
temperatura_ok = np.random.uniform(20.0, 26.0, por_classe)
umidade_ok = np.random.uniform(40.0, 65.0, por_classe)
temperatura_atencao = np.random.uniform(15.0, 35.0, por_classe)
umidade_atencao = np.random.uniform(25.0, 85.0, por_classe)
fora_da_faixa = ((temperatura_atencao < 20.0) | (temperatura_atencao > 26.0) |
                 (umidade_atencao < 40.0) | (umidade_atencao > 65.0))
while not np.all(fora_da_faixa):
    quantidade = np.count_nonzero(~fora_da_faixa)
    temperatura_atencao[~fora_da_faixa] = np.random.uniform(15.0, 35.0, quantidade)
    umidade_atencao[~fora_da_faixa] = np.random.uniform(25.0, 85.0, quantidade)
    fora_da_faixa = ((temperatura_atencao < 20.0) | (temperatura_atencao > 26.0) |
                     (umidade_atencao < 40.0) | (umidade_atencao > 65.0))

temperatura = np.concatenate((temperatura_ok, temperatura_atencao))
umidade = np.concatenate((umidade_ok, umidade_atencao))
rotulo = np.concatenate((np.ones(por_classe), np.zeros(por_classe))).astype(np.float32)
total = len(rotulo)
features = np.column_stack((temperatura, umidade)).astype(np.float32)
indices = np.random.permutation(total)
limite_treino = int(total * 0.8)
treino, teste = indices[:limite_treino], indices[limite_treino:]

with (OUTPUT / "dataset_dht22.csv").open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.writer(arquivo)
    escritor.writerow(["temperatura_c", "umidade_pct", "confortavel"])
    for t, u, y in zip(temperatura, umidade, rotulo):
        escritor.writerow([f"{t:.3f}", f"{u:.3f}", int(y)])

modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(2,)),
    tf.keras.layers.Dense(24, activation="relu"),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
modelo.compile(optimizer=tf.keras.optimizers.Adam(0.01),
               loss="binary_crossentropy", metrics=["accuracy"])
modelo.fit(features[treino], rotulo[treino], epochs=180, batch_size=32,
           validation_split=0.2, verbose=0)
perda, acuracia = modelo.evaluate(features[teste], rotulo[teste], verbose=0)

conversor = tf.lite.TFLiteConverter.from_keras_model(modelo)
conversor.optimizations = [tf.lite.Optimize.DEFAULT]
conversor.representative_dataset = lambda: ([features[i:i + 1]] for i in treino[:200])
conversor.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
conversor.inference_input_type = tf.int8
conversor.inference_output_type = tf.int8
modelo_tflite = conversor.convert()

(OUTPUT / "modelo_dht22_int8.tflite").write_bytes(modelo_tflite)
valores = ", ".join(f"0x{byte:02x}" for byte in modelo_tflite)
(OUTPUT / "model_data.cc").write_text(
    "#include <cstdint>\n\n"
    "extern const unsigned char g_model_dht22[] = {\n" + valores + "\n};\n"
    "extern const int g_model_dht22_len = sizeof(g_model_dht22);\n", encoding="utf-8")
(OUTPUT / "metricas.txt").write_text(
    f"Amostras: {total}\nTreino: {len(treino)}\nTeste: {len(teste)}\n"
    f"Acuracia_teste: {acuracia:.4f}\nPerda_teste: {perda:.4f}\n"
    "Rotulo confortavel: 20-26 C e 40-65 % de umidade.\n", encoding="utf-8")

print("Treinamento concluído")
print(f"Acurácia de teste: {acuracia:.2%}")
print("Arquivos criados em artefatos_dht22/")
