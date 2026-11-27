-- SQL equivalents of the dashboard KPIs (SQLite / PostgreSQL compatible).
-- Table: claims  (load Dataset/processed/claims_clean.csv). Used to cross-check Python and DAX results.

-- 1. Headline KPIs
SELECT COUNT(*)                        AS total_records,
       ROUND(SUM(charges), 2)          AS total_charges,
       ROUND(AVG(charges), 2)          AS average_charge,
       ROUND(MAX(charges), 2)          AS highest_charge
FROM claims;

-- 2. Cost concentration by smoker status
SELECT smoker,
       COUNT(*)                                                    AS records,
       ROUND(SUM(charges), 2)                                      AS total_charges,
       ROUND(AVG(charges), 2)                                      AS average_charge,
       ROUND(100.0 * SUM(charges) / (SELECT SUM(charges) FROM claims), 2) AS pct_of_total_charges
FROM claims
GROUP BY smoker
ORDER BY total_charges DESC;

-- 3. Average charge by age group
SELECT age_group, COUNT(*) AS records, ROUND(AVG(charges), 2) AS average_charge
FROM claims
GROUP BY age_group
ORDER BY age_group;

-- 4. Smoker x obesity segment share of cost
SELECT smoker_bmi_segment,
       COUNT(*)                                                    AS records,
       ROUND(AVG(charges), 2)                                      AS average_charge,
       ROUND(100.0 * SUM(charges) / (SELECT SUM(charges) FROM claims), 2) AS pct_of_total_charges
FROM claims
GROUP BY smoker_bmi_segment
ORDER BY pct_of_total_charges DESC;

-- 5. High-cost records (flag already computed in Python as charges > P90)
SELECT COUNT(*) AS high_cost_records, ROUND(SUM(charges), 2) AS high_cost_charges
FROM claims
WHERE is_high_cost IN ('True', 1, TRUE);

-- 6. Peer anomalies (review candidates, not fraud)
SELECT smoker, age_group, COUNT(*) AS peer_anomalies
FROM claims
WHERE is_peer_anomaly IN ('True', 1, TRUE)
GROUP BY smoker, age_group
ORDER BY peer_anomalies DESC;
