from os.path import dirname, join as pjoin
from scipy.io import wavfile
import pdb
import scipy.io
import math
import random
import matplotlib.pyplot as plt
import numpy as np

# Начальная фаза приёма
start_phase = 167

# Имя входного wav файла
wav_file_in_name = 'BPSK_2100_8_metro_6.wav'
#wav_file_in_name = "bpsk_out_and_noise_and_low_freq.wav"

# Имя выходного файла с данными
data_file_out_name = 'data_rcv.txt'

# Читаем входной файл
input_signal_samplerate, input_signal_data = wavfile.read(wav_file_in_name)
input_signal_length = input_signal_data.shape[0]

# Частота несущей
carrier_frequency = 2100
period_per_bit = 8

# Число отсчётов на один бит данных
sample_per_carrier = (input_signal_samplerate * period_per_bit) / carrier_frequency

# Период семплирования
input_signal_sampletime = 1 / input_signal_samplerate

# Длительность посылки бит
signal_length = len(input_signal_data) * period_per_bit / sample_per_carrier

# Вывод параметров файла
print("Частота дискретизации =", input_signal_samplerate)
print("Число отсчётов =", input_signal_length)
print("Длительность секунд =", input_signal_length/input_signal_samplerate)
print("Число периодов на бит", period_per_bit);
print("Число отсчётов на период синуса =", input_signal_samplerate/carrier_frequency)
print("Число отсчётов на один бит данных =", sample_per_carrier)
print("Длина посылки, бит =", signal_length / period_per_bit)

# Формируем отсчёты косинуса
cos_samples = np.arange(sample_per_carrier)
cos_signal = np.sin(2 * np.pi * cos_samples * period_per_bit / sample_per_carrier)

# Формруем данные с результатом перемножения сигнала на косинус, пока всё 0
output_signal = np.linspace(0, 0, int(input_signal_length))

# Масштабируем входной сигнал, что бы максимум был 1 или -1
scale_value = 1
for i in range(int(input_signal_length)):
    if abs(input_signal_data[i]) > scale_value:
       scale_value = abs(input_signal_data[i])
input_signal_data = input_signal_data/scale_value

#input_signal_data = input_signal_data/32767

# Средние значения сигнала без перемножения, это граница определения 0 или 1
# Вместо границы равной 0, добавил из-за НЧ шума, который смещает сигнал выше или ниже 0
# Это смещение нужно или убрать или сравнивать с ним, делаю второе
mean_values = np.linspace(0, 0, int(signal_length / period_per_bit))

# Считаем средние значения
mean_value = 0
sample_cnt = 0
output_cnt = 0
for i in range(int(input_signal_length)):
    mean_value += (output_signal[i] * input_signal_sampletime)

    # Счётчик отсчётов для периода интегрирования
    sample_cnt += 1
    if(sample_cnt >= sample_per_carrier):
        sample_cnt = 0
        mean_values[output_cnt] = mean_value/sample_per_carrier
        mean_value = 0
        output_cnt += 1

# Перемножаем входной сигнал на косинус
phase_cnt = start_phase # Счётчик фазы косинуса
for i in range(int(input_signal_length)):
    output_signal[i] = cos_signal[phase_cnt] * input_signal_data[i]

    # Счётчик фазы косинуса
    # Здесь же счётчик бит
    phase_cnt += 1
    if(phase_cnt >= sample_per_carrier):
        phase_cnt = 0

# Значения получаемы в результате интегрирования
output_integrator = np.linspace(0, 0, int(signal_length / period_per_bit))

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
output_bit_signal = np.linspace(0, 0, int(signal_length / period_per_bit))

# Превращаем результат интегрирования в биты
for i in range(int(signal_length / period_per_bit)):
    # Всё что больше mean_values[i] это 1, иначе 0
    if output_integrator[i] > mean_values[i]:
        output_bit_signal[i] = 1
    else:
        output_bit_signal[i] = 0

# В строку
output_bit_signal_int8 = np.int8(output_bit_signal)
output_bit_signal_str = ''
for i in range(int(signal_length / period_per_bit)):
    output_bit_signal_str += ' ' + str(output_bit_signal_int8[i])
    
# Записываем файл с данными
#output_bit_signal_str = str(output_bit_signal)
file = open(data_file_out_name, "w")
file.write(output_bit_signal_str)
file.close()

t = np.linspace(1, input_signal_length, input_signal_length)
plt.subplot(3,1,1)
plt.plot(t, output_signal)
plt.title('Input signal')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.show()

t = np.linspace(0, int(signal_length), int(signal_length / period_per_bit))
plt.subplot(3,1,2)
plt.plot(t, output_integrator)
plt.title('Integrator')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.show()

t = np.linspace(0, int(signal_length), int(signal_length / period_per_bit))
plt.subplot(3,1,3)
plt.plot(t, output_bit_signal)
plt.title('Output bit stream')
plt.ylabel('Bit')
plt.xlabel('Time (s)')
plt.show()
