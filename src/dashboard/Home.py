import pandas as pd
import streamlit as st


st.set_page_config(layout="wide")

st.write("Hello World")

def load_data():
    data = pd.read_feather('datasets/final/nus_knn_eval.feather')
    data['dt'] = pd.to_datetime(data['dt'])
    return data


metrics_data = load_data().reset_index(drop=True)
st.write(metrics_data)

def get_summary_metric_for_model(data, model, metric):
    model_data = data[data['model'] == model]
    model_data_latest_metric = model_data.nlargest(1, 'dt').iloc[-1][metric].squeeze()
    model_data_previous_metric = model_data.nlargest(2, 'dt').iloc[-1][metric].squeeze()

    pct_improvement = (model_data_latest_metric - model_data_previous_metric) / model_data_previous_metric

    return [round(model_data_latest_metric, 2), f"{round(100 * pct_improvement, 0)}%"]

def filter_data(data, models):
    mask = data['model'].isin(models)
    
    return data.copy()[mask]

def get_chart_data_for_multiple_models(data, models, metrics):
    new_df = pd.DataFrame(index=data['dt'].unique())
    filtered_data = data.copy()
    for model in models:
        suffix = f'_{model}'
        model_data = filtered_data[filtered_data['model'] == model].set_index('dt')
        model_data = model_data[metrics]
        model_data.columns = [col + suffix for col in model_data.columns]
        new_df = pd.concat([new_df, model_data], axis=1) 

    return new_df