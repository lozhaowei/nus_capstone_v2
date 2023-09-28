import streamlit as st
import pandas as pd

from Home import load_data, get_summary_metric_for_model, filter_data, get_chart_data_for_multiple_models

st.set_page_config(layout='wide')

data = load_data().reset_index(drop=True)
model_list = data['model'].unique()

col1, col2 = st.columns(2)
col1.title('Videos')
models = col2.multiselect('Model', options=model_list, default=model_list[0])
filtered_data = filter_data(data, models)

st.divider()

precision_metric = get_summary_metric_for_model(filtered_data, models[0], 'precision')
recall_metric = get_summary_metric_for_model(filtered_data, models[0], 'recall')
f1_metric = get_summary_metric_for_model(filtered_data, models[0], 'f1 score')

col1, col2, col3 = st.columns(3)
col1.metric("Precision", precision_metric[0], precision_metric[1])
col2.metric("Recall", recall_metric[0], recall_metric[1])
col3.metric("F1 Score", f1_metric[0], f1_metric[1])

st.divider()

if st.checkbox('Show metrics results'):
    st.write('Metrics Data')
    filtered_data

col1, col2 = st.columns(2)
col1.subheader('Line chart')
metrics = col2.multiselect('Metrics', options=['Precision', 'Recall', 'Accuracy', 'F1 Score', 'ROC AUC Score', 'HitRatio@K', 'NDCG@K'],
                           default='ROC AUC Score')
metrics_lowercase = [string.lower() for string in metrics]

if len(models) == 1:
    line_chart_data = filtered_data[metrics_lowercase + ['datetime']].set_index('datetime')
    columns_to_plot = metrics_lowercase
else:
    line_chart_data = get_chart_data_for_multiple_models(data, models, metrics_lowercase)
    columns_to_plot = line_chart_data.columns
    
st.line_chart(line_chart_data, y=columns_to_plot)