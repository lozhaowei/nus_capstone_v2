import pymysql
import pandas as pd
import streamlit as st
from decouple import config

from src.data import database

CONN_PARAMS = {
    'host': config('DB_HOST'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'port': int(config('DB_PORT')),
    'database': config('DB_NAME'),
}

def get_dashboard_data(entity):
    """
    queries database to obtain metrics data of specific model, renames the columns for frontend use
    :param entity: recommended item
    """
    try:
        query = f"SELECT * FROM nus_{entity}_eval"
        df = database.query_database(query)
        df["dt"] = pd.to_datetime(df["dt"])

        # Rename columns for frontend use
        df.rename(columns={'roc_auc_score': 'ROC AUC Score', 'accuracy': 'Accuracy', 'precision': 'Precision',
                           'recall': 'Recall', 'f1_score': 'F1 Score', 'hit_ratio_k': 'HitRatio@K',
                           'ndcg_k': 'NDCG@K'}, inplace=True)

        return df

    except Exception as e:
        print("Error:", e)

@st.cache_data
def get_upvote_percentage_for_user(recommendation_table_name):
    """
    Queries database for latest 3 dates in the list of recommendations produced by the model, for use in the "Latest Model Metrics" section.
    Args:
    :param recommendation_table_name: Name of table in AWS database to query from. Table should contain the recommendations produced by the relevant model,
    together with the date it was produced at.
    """
    try:
        conn = pymysql.connect(**CONN_PARAMS)
        cursor = conn.cursor()

        query = """
        SELECT user_id, SUM(upvote_count) as upvoted_videos, COUNT(upvote_count) as number_recommended, SUM(upvote_count) / COUNT(upvote_count) as upvote_percentage
        FROM (
            SELECT *,
                CASE
                    WHEN t1.timestamp > t1.created_at THEN 1
                    ELSE 0
                    END AS upvote_count
            FROM (
                SELECT rdv.user_id, rdv.recommended_video_id, v.video_id, v.status, rdv.created_at, v.timestamp
                FROM rs_daily_video_for_user rdv
                        LEFT JOIN vote v
                                    ON rdv.recommended_video_id = v.video_id
                                        AND rdv.user_id = v.voter_id) t1
                    WHERE DATE(t1.created_at) = '2023-09-05' AND DATE(t1.timestamp) = '2023-09-05'
            ) t2 
            GROUP BY user_id
            ORDER BY upvote_percentage DESC;
        """

        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description]).set_index("user_id")

        return df

    except Exception as e:
        print("Error, ", e)

def get_individual_user_visualisation(user_id):
    try:
        conn = pymysql.connect(**CONN_PARAMS)
        cursor = conn.cursor()

        query = f"""
        SELECT
            voter_id,
            SUM(CASE WHEN category = 'OTHERS' THEN 1 ELSE 0 END) AS Others,
            SUM(CASE WHEN category = 'DANCE' THEN 1 ELSE 0 END) AS Dance,
            SUM(CASE WHEN category = 'ART&DESIGN' THEN 1 ELSE 0 END) AS ArtandDesign,
            SUM(CASE WHEN category = 'STYLE&BEAUTY' THEN 1 ELSE 0 END) AS StyleandBeauty,
            SUM(CASE WHEN category = 'MUSIC' THEN 1 ELSE 0 END) AS Music,
            SUM(CASE WHEN category = 'COMEDY' THEN 1 ELSE 0 END) AS Comedy,
            SUM(CASE WHEN category = 'LIFESTYLE' THEN 1 ELSE 0 END) AS Lifestyle,
            SUM(CASE WHEN category = 'FOOD&DRINKS' THEN 1 ELSE 0 END) AS FoodandDrinks,
            SUM(CASE WHEN category = 'SPORTS&FITNESS' THEN 1 ELSE 0 END) AS SportsandFitness,
            SUM(CASE WHEN category = 'GAMING' THEN 1 ELSE 0 END) AS Gaming,
            SUM(CASE WHEN category = 'NFT' THEN 1 ELSE 0 END) AS NFT,
            SUM(CASE WHEN category = 'HACKS&PRODUCTIVITY' THEN 1 ELSE 0 END) AS HacksandProductivity
        FROM
            (SELECT v.voter_id, s.category 
            FROM vote v
            LEFT JOIN season s
            ON v.season_id = s.id) AS subquery
        GROUP BY voter_id
        HAVING voter_id = '{user_id}'
        """

        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

        return df
    
    except Exception as e:
        print("Error, ", e)

def get_recommended_video_info(user_id):
    try:
        conn = pymysql.connect(**CONN_PARAMS)
        cursor = conn.cursor()

        query = f"""
        SELECT 
            user_id,
            SUM(CASE WHEN category = 'OTHERS' THEN 1 ELSE 0 END) AS Others,
            SUM(CASE WHEN category = 'DANCE' THEN 1 ELSE 0 END) AS Dance,
            SUM(CASE WHEN category = 'ART&DESIGN' THEN 1 ELSE 0 END) AS ArtandDesign,
            SUM(CASE WHEN category = 'STYLE&BEAUTY' THEN 1 ELSE 0 END) AS StyleandBeauty,
            SUM(CASE WHEN category = 'MUSIC' THEN 1 ELSE 0 END) AS Music,
            SUM(CASE WHEN category = 'COMEDY' THEN 1 ELSE 0 END) AS Comedy,
            SUM(CASE WHEN category = 'LIFESTYLE' THEN 1 ELSE 0 END) AS Lifestyle,
            SUM(CASE WHEN category = 'FOOD&DRINKS' THEN 1 ELSE 0 END) AS FoodandDrinks,
            SUM(CASE WHEN category = 'SPORTS&FITNESS' THEN 1 ELSE 0 END) AS SportsandFitness,
            SUM(CASE WHEN category = 'GAMING' THEN 1 ELSE 0 END) AS Gaming,
            SUM(CASE WHEN category = 'NFT' THEN 1 ELSE 0 END) AS NFT,
            SUM(CASE WHEN category = 'HACKS&PRODUCTIVITY' THEN 1 ELSE 0 END) AS HacksandProductivity
        FROM (
            SELECT rdv.user_id, rdv.recommended_video_id, v.season_id, s.category
            FROM (
                rs_daily_video_for_user rdv 
                LEFT JOIN video v ON rdv.recommended_video_id = v.id
                LEFT JOIN season s ON v.season_id = s.id
            )
            WHERE DATE(rdv.created_at) = '2023-09-05'
        ) t1
        GROUP BY user_id
        HAVING user_id = '{user_id}';
        """

        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

        return df
    
    except Exception as e:
        print("Error, ", e)

def insert_model_feedback(data):
    """
    only inserts one row at a time into nus_model_feedback table
    :param data: dictionary - column names are keys: rating, feedback, model, recommended_item
    :return: 0 if success, 1 if failed
    """
    if data is None:
        print("Error getting feedback data")
        return 1

    if len(data['feedback']) > 500:
        print("Feedback length cannot exceed 500 char")
        return 1

    try:
        conn = pymysql.connect(**CONN_PARAMS)
        cursor = conn.cursor()

        insert_query = f"INSERT INTO nus_model_feedback (rating, feedback, model, recommended_item) " \
                       f"VALUES ({data['rating']}, '{data['feedback']}', '{data['model']}', " \
                       f"'{data['recommended_item']}')"

        print(insert_query)
        cursor.execute(insert_query, data)

        conn.commit()
        conn.close()

        print(f"Data inserted into MySQL table nus_model_feedback successfully.")
        return 0

    except Exception as e:
        print("Error:", e)
        return 1

def get_model_ratings(recommended_item):
    """
    calculates the average rating for each model based on the recommended item
    :param recommended_item: recommended item: video, conversation, must follow the format: lowercase, singular
    :return: returns a dictionary: keys - model name, rating - average rating
    if error fetching data, returns an empty dictionary
    """
    try:
        conn = pymysql.connect(**CONN_PARAMS)
        cursor = conn.cursor()

        query = f"SELECT model, FORMAT(AVG(rating), 2) FROM nus_model_feedback " \
                f"WHERE recommended_item = %s" \
                f"GROUP BY model;"

        cursor.execute(query, recommended_item)
        result = cursor.fetchall()

        conn.close()

        # return result example: (('knn', '4.25'), ('random_forest', '4.50'))
        return {model: rating for (model, rating) in result}

    except Exception as e:
        print("Error:", e)
