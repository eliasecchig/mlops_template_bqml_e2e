WITH joined_transactions AS (
    SELECT
    raw_tx.tx_ts,
    raw_tx.tx_id,
    raw_tx.customer_id,
    raw_tx.terminal_id,
    raw_tx.tx_amount,
    raw_lb.tx_fraud
    FROM `tx.tx` AS raw_tx
    LEFT JOIN `tx.txlabels` AS raw_lb
    ON raw_tx.TX_ID = raw_lb.TX_ID
)
SELECT *,
FORMAT_DATE('%A', tx_ts)  AS day_of_the_week,
COUNT(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 7200 PRECEDING AND 1 PRECEDING) AS count_tx_amount_by_customer_id_2h_1s,
COUNT(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 21600 PRECEDING AND 1 PRECEDING) AS count_tx_amount_by_customer_id_6h_1s,
COUNT(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 518400 PRECEDING AND 1 PRECEDING) AS count_tx_amount_by_customer_id_6d_1s,
COUNT(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 2419200 PRECEDING AND 1 PRECEDING) AS count_tx_amount_by_customer_id_28d_1s,
COUNT(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 7776000 PRECEDING AND 1 PRECEDING) AS count_tx_amount_by_customer_id_90d_1s,
CAST(SUM(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 7200 PRECEDING AND 1 PRECEDING) AS FLOAT64) AS sum_tx_amount_by_customer_id_2h_1s,
CAST(SUM(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 21600 PRECEDING AND 1 PRECEDING) AS FLOAT64) AS sum_tx_amount_by_customer_id_6h_1s,
CAST(SUM(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 518400 PRECEDING AND 1 PRECEDING) AS FLOAT64) AS sum_tx_amount_by_customer_id_6d_1s,
CAST(SUM(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 2419200 PRECEDING AND 1 PRECEDING) AS FLOAT64) AS sum_tx_amount_by_customer_id_28d_1s,
CAST(SUM(tx_amount) OVER (PARTITION BY customer_id ORDER BY UNIX_SECONDS(tx_ts) RANGE BETWEEN 7776000 PRECEDING AND 1 PRECEDING) AS FLOAT64) AS sum_tx_amount_by_customer_id_90d_1s,
FROM joined_transactions
-- We select a part of our data for training, in this case anything more recent than a year
WHERE DATE(tx_ts) > DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
-- We limit for demo purposes
LIMIT 10000
