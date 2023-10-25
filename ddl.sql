--Postgres Schema DDL
DROP TABLE stg_wine_quality;
CREATE TABLE IF NOT EXISTS stg_wine_quality
(
    fixed_acidity        REAL,
    volatile_acidity     REAL,
    citric_acid          REAL,
    residual_sugar       REAL,
    chlorides            REAL,
    free_sulfur_dioxide  REAL,
    total_sulfur_dioxide REAL,
    pH                   REAL,
    sulphates            REAL,
    alcohol              REAL,
    alcohol_level        VARCHAR(6)
);

-- ClickHouse Schema DDL
CREATE TABLE homebase_assignment.wine_quality
(
    fixed_acidity        Float64,
    volatile_acidity     Float64,
    citric_acid          Float64,
    residual_sugar       Float64,
    chlorides            Float64,
    free_sulfur_dioxide  Float64,
    total_sulfur_dioxide Float64,
    density              Float64,
    pH                   Float64,
    sulphates            Float64,
    alcohol              Float64,
    alcohol_level        String
)
    engine = MergeTree ORDER BY alcohol;