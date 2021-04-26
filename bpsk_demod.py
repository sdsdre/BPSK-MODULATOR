from os.path import dirname, join as pjoin
from scipy.io import wavfile
import pdb
import scipy.io
import math
import random
import matplotlib.pyplot as plt
import numpy as np

# Имя входного wav файла
wav_file_in_name = 'bpsk_out_and_noise.wav'

# Имя выходного файла с данными
data_file_out_name = 'data_rcv.txt'

# Читаем входной файл
input_signal_samplerate, input_signal_data = wavfile.read(wav_file_in_name)
input_signal_length = input_signal_data.shape[0]

# Частота несущей
carrier_frequency = 2940

# Число отсчётов на один бит данных
sample_per_carrier = input_signal_samplerate / carrier_frequency

# Период семплирования
input_signal_sampletime = 1 / input_signal_samplerate

# Длительность посылки бит
signal_length = len(input_signal_data) / sample_per_carrier

# Вывод параметров файла
print("Частота дискретизации =", input_signal_samplerate)
print("Число отсчётов =", input_signal_length)
print("Длительность секунд =", input_signal_length/input_signal_samplerate)
print("Число отсчётов на период несущей =", sample_per_carrier)
print("Длина посылки, бит =", signal_length)

# Формируем отсчёты косинуса
cos_samples = np.arange(input_signal_samplerate / carrier_frequency)
cos_signal = np.sin(2 * np.pi * carrier_frequency * cos_samples / input_signal_samplerate)

# Формруем данные с результатом перемножения сигнала на косинус, пока всё 0
output_signal = np.linspace(0, 0, int(input_signal_length))

# Масштабируем входной сигнал
input_signal_data = input_signal_data/32767

# Перемножаем входной сигнал на косинус
phase_cnt = 0 # Счётчик фазы косинуса
for i in range(int(input_signal_length)):
    output_signal[i] = cos_signal[phase_cnt] * input_signal_data[i]

    # Счётчик фазы косинуса
    # Здесь же счётчик бит
    phase_cnt += 1
    if(phase_cnt >= sample_per_carrier):
        phase_cnt = 0

# Значения получаемы в результате интегрирования
output_integrator = np.linspace(0, 0, int(signal_length))

# Интегрируем отсчёты
mean_value = 0
sample_cnt = 0
output_cnt = 0
for i in range(int(input_signal_length)):
    mean_value += (output_signal[i] * input_signal_sampletime)

    # Счётчик отсчётов для периода интегрирования
    sample_cnt += 1
    if(sample_cnt >= sample_per_carrier):
        sample_cnt = 0
        output_integrator[output_cnt] = mean_value/sample_per_carrier
        mean_value = 0
        output_cnt += 1

# Значения бит
output_bit_signal = np.linspace(0, 0, int(signal_length))

# Превращаем результат интегрирования в биты
for i in range(int(signal_length)):
    # Всё что больше 0 это 1, иначе 0
    if output_integrator[i] > 0:
        output_bit_signal[i] = 1
    else:
        output_bit_signal[i] = 0

# В строку
output_bit_signal_int8 = np.int8(output_bit_signal)
output_bit_signal_str = ''
for i in range(int(signal_length)):
    output_bit_signal_str += ' ' + str(output_bit_signal_int8[i])
    
# Записываем файл с данными
#output_bit_signal_str = str(output_bit_signal)
file = open(data_file_out_name, "w")
file.write(output_bit_signal_str)
file.close()

t = np.linspace(1, input_signal_length, input_signal_length)
plt.subplot(3,1,1)
plt.plot(t, output_signal)
plt.title('Signal')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.show()

t = np.linspace(0, int(signal_length), int(signal_length))
plt.subplot(3,1,2)
plt.plot(t, output_integrator)
plt.title('Signal')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.show()

t = np.linspace(0, int(signal_length), int(signal_length))
plt.subplot(3,1,3)
plt.plot(t, output_bit_signal)
plt.title('Signal')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.show()
