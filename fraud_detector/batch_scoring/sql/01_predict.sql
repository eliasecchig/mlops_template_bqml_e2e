SELECT * FROM ML.PREDICT(MODEL `{{ model_name }}`, (
SELECT *
FROM
tx.feature_table_scoring))
