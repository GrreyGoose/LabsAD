import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup, Select, Button

INITIAL_AMPLITUDE = 1.0
INITIAL_FREQUENCY = 1.0
INITIAL_PHASE = 0.0
INITIAL_NOISE_MEAN = 0.0
INITIAL_NOISE_COVARIANCE = 0.1
INITIAL_SHOW_NOISE = True
INITIAL_FILTER_WINDOW = 5

t = np.linspace(0, 10, 500)

last_noise_mean = INITIAL_NOISE_MEAN
last_noise_cov = INITIAL_NOISE_COVARIANCE
current_noise = np.random.normal(INITIAL_NOISE_MEAN, np.sqrt(INITIAL_NOISE_COVARIANCE), len(t))

def harmonic_with_noise(amplitude, frequency, phase, noise_to_use, show_noise):
    harmonic = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    if show_noise:
        return harmonic + noise_to_use
    else:
        return harmonic

def moving_average_filter(data, window_size):
    if window_size < 1:
        return data
    window_size = int(window_size) // 2 * 2 + 1
    weights = np.repeat(1.0, window_size) / window_size
    return np.convolve(data, weights, 'same')

source_original = ColumnDataSource(data=dict(x=t, y=t))
source_filtered = ColumnDataSource(data=dict(x=t, y=t))

plot_original = figure(height=300, width=800, title="Вихідний сигнал",
                       tools="crosshair,pan,reset,save,wheel_zoom",
                       x_range=[0, 10], y_range=[-6, 6])
plot_original.line('x', 'y', source=source_original, line_width=2, line_alpha=0.8, color='blue')
plot_original.title.text_font_size = '14pt'
plot_original.xaxis.axis_label = "Час"
plot_original.yaxis.axis_label = "Амплітуда"

plot_filtered = figure(height=300, width=800, title="Відфільтрований сигнал",
                       tools="crosshair,pan,reset,save,wheel_zoom",
                       x_range=[0, 10], y_range=[-6, 6])
plot_filtered.line('x', 'y', source=source_filtered, line_width=2, line_alpha=0.8, color='red')
plot_filtered.title.text_font_size = '14pt'
plot_filtered.xaxis.axis_label = "Час"
plot_filtered.yaxis.axis_label = "Амплітуда"

amp_slider = Slider(title="Амплітуда", value=INITIAL_AMPLITUDE, start=0.1, end=5.0, step=0.1)
freq_slider = Slider(title="Частота", value=INITIAL_FREQUENCY, start=0.1, end=5.0, step=0.1)
phase_slider = Slider(title="Фаза (радіани)", value=INITIAL_PHASE, start=0, end=2 * np.pi, step=0.1)

show_noise_check = CheckboxGroup(labels=["Показувати шум"], active=[0] if INITIAL_SHOW_NOISE else [])

noise_mean_slider = Slider(title="Середнє шуму", value=INITIAL_NOISE_MEAN, start=-1.0, end=1.0, step=0.1)
noise_cov_slider = Slider(title="Дисперсія шуму", value=INITIAL_NOISE_COVARIANCE, start=0.0, end=1.0, step=0.05)

filter_select = Select(title="Тип фільтра:", value="none", options=[("none", "Без фільтра"), ("ma", "Ковзне середнє")])
filter_window_slider = Slider(title="Розмір вікна фільтра:", value=INITIAL_FILTER_WINDOW, start=1, end=51, step=2)

reset_button = Button(label="Скинути параметри", button_type="danger")

def update_data(attr, old, new):
    global current_noise, last_noise_mean, last_noise_cov

    amp = amp_slider.value
    freq = freq_slider.value
    phase = phase_slider.value
    show_noise = len(show_noise_check.active) > 0
    nm = noise_mean_slider.value
    nc = noise_cov_slider.value
    filter_type = filter_select.value
    filter_window = filter_window_slider.value

    if nm != last_noise_mean or nc != last_noise_cov:
        current_noise = np.random.normal(nm, np.sqrt(nc), len(t))
        last_noise_mean = nm
        last_noise_cov = nc

    y_original = harmonic_with_noise(amp, freq, phase, current_noise, show_noise)

    if filter_type == 'ma':
        y_filtered = moving_average_filter(y_original, filter_window)
        filter_window_slider.disabled = False
    else:
        y_filtered = y_original
        filter_window_slider.disabled = True

    source_original.data = dict(x=t, y=y_original)
    source_filtered.data = dict(x=t, y=y_filtered)

def reset_all():
    global current_noise, last_noise_mean, last_noise_cov

    amp_slider.value = INITIAL_AMPLITUDE
    freq_slider.value = INITIAL_FREQUENCY
    phase_slider.value = INITIAL_PHASE
    show_noise_check.active = [0] if INITIAL_SHOW_NOISE else []
    noise_mean_slider.value = INITIAL_NOISE_MEAN
    noise_cov_slider.value = INITIAL_NOISE_COVARIANCE
    filter_select.value = "none"
    filter_window_slider.value = INITIAL_FILTER_WINDOW

    last_noise_mean = INITIAL_NOISE_MEAN
    last_noise_cov = INITIAL_NOISE_COVARIANCE
    current_noise = np.random.normal(INITIAL_NOISE_MEAN, np.sqrt(INITIAL_NOISE_COVARIANCE), len(t))

    update_data(None, None, None)

widgets_to_watch = [
    amp_slider, freq_slider, phase_slider,
    noise_mean_slider, noise_cov_slider,
    filter_window_slider
]
for widget in widgets_to_watch:
    widget.on_change('value', update_data)

show_noise_check.on_change('active', update_data)
filter_select.on_change('value', update_data)
reset_button.on_click(reset_all)

controls = column(
    amp_slider, freq_slider, phase_slider,
    show_noise_check, noise_mean_slider, noise_cov_slider,
    filter_select, filter_window_slider,
    reset_button,
    width=350
)

plots = column(plot_original, plot_filtered)

layout = row(controls, plots)

reset_all()

curdoc().add_root(layout)
curdoc().title = "Гармоніка з шумом"