import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

def graficar_historial(history):
    """Grafica el historial de entrenamiento (loss y MAE) y guarda la imagen."""
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Loss vs. Epochs", "MAE vs. Epochs"))

    # Gráfica de Loss
    fig.add_trace(go.Scatter(
        x=list(range(len(history['loss']))),
        y=history['loss'],
        mode='lines',
        name='Training Loss'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=list(range(len(history['val_loss']))),
        y=history['val_loss'],
        mode='lines',
        name='Validation Loss'
    ), row=1, col=1)

    # Gráfica de MAE
    fig.add_trace(go.Scatter(
        x=list(range(len(history['mae']))),
        y=history['mae'],
        mode='lines',
        name='Training MAE'
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=list(range(len(history['val_mae']))),
        y=history['val_mae'],
        mode='lines',
        name='Validation MAE'
    ), row=1, col=2)

    fig.update_layout(
        title_text='Training History',
        xaxis_title='Epochs',
        yaxis_title='Loss',
        yaxis2=dict(
            title='MAE',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            font=dict(size=10),
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        )
    )

    # fig.write_image('../img/graficas_dl.png')
    # fig.show()

    return fig