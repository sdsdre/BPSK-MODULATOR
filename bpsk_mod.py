from os.path import dirname, join as pjoin
from scipy.io import wavfile
import pdb
import scipy.io
import math
import random
import matplotlib.pyplot as plt
import numpy as np

# Имя файла с данными
data_file_name = 'data.txt'

# Имя выходного wav файла
wav_file_name = 'bpsk_out.wav'

# Параметры файла wav
samplerate = 44100
carrier_frequency = 2940

# Число отсчётов на один бит данных
sample_per_carrier = samplerate / carrier_frequency

# Вывод параметров
print("Частота дискретизации wav =", samplerate)
print("Частота несущей =", carrier_frequency)
print("Число отсчётов на период несущей =", sample_per_carrier)

# Читаем файл с данными
with open(data_file_name) as fdata:
    data_list = [int(x) for x in next(fdata).split()]

# Ковертируем в int
data_array = np.array(data_list, dtype = np.int32())

"""
# Относительное кодирование потока бит
# Всё что больше 0 это 1, меньше или равно 0 это 0
for bit in enumerate(data_array):
    if bit[1] > 0:
        data_array[bit[0]] = 1
    else:
        data_array[bit[0]] = 0

# Зададим начальное значение для относительного кодирования
prev_bit = 0
bit_value = 0

# Само относительное кодирование, складываем
for bit in enumerate(data_array):
    bit_value = data_array[bit[0]]
    data_array[bit[0]] = prev_bit ^ data_array[bit[0]]
    prev_bit = bit_value
"""

# Преобразуем поток бит в знаковый
# Всё что больше 0 это 1, меньше это -1
for bit in enumerate(data_array):
    if bit[1] > 0:
        data_array[bit[0]] = 1
    else:
        data_array[bit[0]] = -1

# Длительность посылки
signal_length = sample_per_carrier * len(data_array)
print("Длина посылки, бит =", len(data_array))
print("Число отсчётов посылки =", signal_length)
print("Длина посылки, секунд =", len(data_array)/carrier_frequency)

# Формируем отсчёты косинуса
cos_samples = np.arange(samplerate / carrier_frequency)
cos_signal = np.sin(2 * np.pi * carrier_frequency * cos_samples / samplerate)

# Формруем выходные данные, пока всё 0
output_signal = np.linspace(0, 0, int(signal_length))

# Формируем выходной сигнал согласно битам, используя BPSK
phase_cnt = 0 # Счётчик фазы косинуса
bit_cnt = 0 # Счётчик бит
bit_sign = 1
for i in range(int(signal_length)):
    bit_sign = data_array[bit_cnt] # Значение бита
    output_signal[i] = cos_signal[phase_cnt] * bit_sign # Формируем сигнал как косинус умноженый на знак бита
    
    # Счётчик фазы косинуса
    # Здесь же счётчик бит
    phase_cnt += 1
    if(phase_cnt >= sample_per_carrier):
        phase_cnt = 0
        bit_cnt += 1
    

# Сохраним в файл
output_signal*= 32767
ountput_signal_int = np.int16(output_signal)
wavfile.write(wav_file_name, samplerate, ountput_signal_int)

#fs = 48000
#datarate = 4410

#f = 4410
#t = 10

#samples = np.linspace(0, t, int(fs*t), endpoint=False)

#signal = np.sin(2 * np.pi * f * samples)

#signal *= 32767

#signal = np.int16(signal)

#wavfile.write("out.wav", fs, signal)
