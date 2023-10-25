--ClickHouse Queries
SELECT count(DISTINCT alcohol) AS unique_values_count
FROM wine_quality;

SELECT alcohol_level, avg(citric_acid) AS average_citric_acid
FROM wine_quality
GROUP BY alcohol_level;
