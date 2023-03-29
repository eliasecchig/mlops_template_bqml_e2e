CREATE OR REPLACE MODEL `{{ model_name }}`
        OPTIONS (
            MODEL_TYPE='LOGISTIC_REG',
            INPUT_LABEL_COLS=['tx_fraud'],
            EARLY_STOP=TRUE,
            MAX_ITERATIONS={{ model_parameters['max_iterations'] }},
            model_registry='vertex_ai',
            vertex_ai_model_id='fraud_detector',
            vertex_ai_model_version_aliases=['experimental','{{ now().strftime('%Y_%m_%d') }}']
        )
        AS SELECT * FROM tx.feature_table
