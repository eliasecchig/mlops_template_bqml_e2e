SELECT * FROM ML.EXPLAIN_PREDICT(MODEL `{{ model_name }}`, (
SELECT *
FROM
tx.feature_table
LIMIT 1000), STRUCT())