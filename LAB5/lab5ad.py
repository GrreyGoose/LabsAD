import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import numpy as np
from scipy.signal import butter, filtfilt

#ФУНКЦІЇ

def harmonic(t, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * t + phase)

def create_noise(t, noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(t))

def harmonic_with_noise(t, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, show_noise=True, noise=None):
    harmonic_signal = harmonic(t, amplitude, frequency, phase)
    if noise is not None and show_noise:
        return harmonic_signal + noise
    elif show_noise:
        global noise_g
        noise_g = create_noise(t, noise_mean, noise_covariance)
        return harmonic_signal + noise_g
    else:
        return harmonic_signal

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff_freq, fs, order=5):
    b, a = butter_lowpass(cutoff_freq, fs, order=order)
    return filtfilt(b, a, data)

#ПОЧАТКОВІ ПАРАМЕТРИ

initial_amplitude = 1.0
initial_frequency = 1.0
initial_phase = 0.0
initial_noise_mean = 0.0
initial_noise_covariance = 0.1
initial_cutoff_frequency = 3.0
noise_g = None

t = np.linspace(0, 10, 1000)
sampling_frequency = 1 / (t[1] - t[0])

#ГРАФІЧНИЙ ІНТЕРФЕЙС

fig, ax = plt.subplots()
fig.set_facecolor('#e0f2f7')
ax.grid(linestyle='--')
ax.set_facecolor('#f0f8ff')
ax.set_ylim(-5, 5)
ax.set_title("Гармоніка, шум і фільтрований сигнал", color='#2e7d32')
plt.subplots_adjust(left=0.12, bottom=0.45, top=0.95)

#Початкові графіки

s_noise = create_noise(t, initial_noise_mean, initial_noise_covariance)
noise_g = s_noise

with_noise_line, = ax.plot(t, harmonic_with_noise(t, initial_amplitude, initial_frequency, initial_phase, noise=noise_g, show_noise=True), lw=2, color='#64b5f6', label='Сигнал з шумом')
filtered_signal = lowpass_filter(with_noise_line.get_ydata(), initial_cutoff_frequency, sampling_frequency)
l_filtered, = ax.plot(t, filtered_signal, lw=2, color='#1976d2', linestyle='-', label='Відфільтрований сигнал')
harmonic_line, = ax.plot(t, harmonic(t, initial_amplitude, initial_frequency, initial_phase), lw=2, color='#ff9800', linestyle='-.', label='Гармонічний сигнал')

ax.legend(facecolor='#e3f2fd', edgecolor='#bbdefb')

#СЛАЙДЕРИ

axcolor = '#b0bec5'
slider_color = '#546e7a'

ax_amplitude = plt.axes([0.12, 0.35, 0.65, 0.03], facecolor=axcolor)
ax_frequency = plt.axes([0.12, 0.3, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.12, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.12, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_noise_covariance = plt.axes([0.12, 0.15, 0.65, 0.03], facecolor=axcolor)
ax_cutoff_frequency = plt.axes([0.12, 0.1, 0.65, 0.03], facecolor=axcolor)

s_amplitude = Slider(ax_amplitude, 'Амплітуда', 0.1, 5.0, valinit=initial_amplitude, color=slider_color)
s_frequency = Slider(ax_frequency, 'Частота', 0.1, 5.0, valinit=initial_frequency, color=slider_color)
s_phase = Slider(ax_phase, 'Фаза', 0.0, 2 * np.pi, valinit=initial_phase, color=slider_color)
s_noise_mean = Slider(ax_noise_mean, 'Сер. знач. шуму', -1.0, 1.0, valinit=initial_noise_mean, color=slider_color)
s_noise_covariance = Slider(ax_noise_covariance, 'Ков. шуму', 0.01, 1.0, valinit=initial_noise_covariance, color=slider_color)
s_cutoff_frequency = Slider(ax_cutoff_frequency, 'Част. зрізу', 0.1, 10.0, valinit=initial_cutoff_frequency, color=slider_color)

#ЧЕКБОКС + КНОПКИ

cb_show_noise = CheckButtons(plt.axes([0.83, 0.35, 0.1, 0.04], facecolor=axcolor), ['Показати шум'], [True])
button_regenerate_noise = Button(plt.axes([0.83, 0.275, 0.1, 0.04]), 'Згенерувати шум', color=axcolor, hovercolor='#90a4ae')
button_reset = Button(plt.axes([0.83, 0.125, 0.1, 0.04]), 'Скинути', color=axcolor, hovercolor='#90a4ae')

#ФУНКЦІЇ ОНОВЛЕННЯ

def update(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))

    with_noise_line.set_ydata(
        harmonic_with_noise(t, amplitude, frequency, phase, noise=noise_g, show_noise=cb_show_noise.get_status()[0])
    )

    cutoff_frequency = s_cutoff_frequency.val
    filtered = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered)
    fig.canvas.draw_idle()

def update_noise(val):
    global noise_g
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    noise_mean = s_noise_mean.val
    noise_covariance = s_noise_covariance.val

    noise_g = create_noise(t, noise_mean, noise_covariance)

    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))
    with_noise_line.set_ydata(
        harmonic_with_noise(t, amplitude, frequency, phase, noise_mean, noise_covariance, cb_show_noise.get_status()[0], noise_g)
    )

    filtered = lowpass_filter(with_noise_line.get_ydata(), s_cutoff_frequency.val, sampling_frequency)
    l_filtered.set_ydata(filtered)
    fig.canvas.draw_idle()

def update_filter(val):
    filtered = lowpass_filter(with_noise_line.get_ydata(), s_cutoff_frequency.val, sampling_frequency)
    l_filtered.set_ydata(filtered)
    fig.canvas.draw_idle()

def update_chb(val):
    update(None)

def regenerate_noise(event):
    update_noise(None)

def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_cutoff_frequency.reset()

    s_noise_mean.reset()
    s_noise_covariance.reset()

    #cb_show_noise.set_active(0)

    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    cutoff_frequency = s_cutoff_frequency.val

    harmonic_line.set_ydata(harmonic(t, amplitude, frequency, phase))

    with_noise_line.set_ydata(
        harmonic_with_noise(t, amplitude, frequency, phase, noise=noise_g, show_noise=cb_show_noise.get_status()[0])
    )

    filtered = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered)

    fig.canvas.draw_idle()

#ПОДІЇ

s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update_noise)
s_noise_covariance.on_changed(update_noise)
s_cutoff_frequency.on_changed(update_filter)
cb_show_noise.on_clicked(update_chb)
button_regenerate_noise.on_clicked(regenerate_noise)
button_reset.on_clicked(reset)

plt.show()