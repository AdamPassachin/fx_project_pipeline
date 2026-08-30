-- How many DKK was 1 SEK worth in 2019-01-02?
SELECT
    rate_date,
    base_currency,
    quote_currency,
    rate
FROM
    fact_fx_rate
WHERE
    rate_date = DATE '2019-01-02' AND base_currency = 'SEK' AND quote_currency = 'DKK'

-- Highest SEK rate against EUR with additional information

SELECT
  f.rate_date,
  f.base_currency,
  f.quote_currency,
  f.rate,
  d.currency_name
FROM 
  fact_fx_rate as f
JOIN dim_currency as d
  ON f.base_currency = d.currency_code
JOIN dim_currency as dim
  ON f.quote_currency = dim.currency_code
WHERE
  f.base_currency = 'SEK' AND f.quote_currency = 'EUR'
ORDER BY f.rate DESC 

-- Highest EUR rate for each currency
WITH ranked_rates AS (
  SELECT
    rate_date,
    base_currency,
    quote_currency,
    rate,
    ROW_NUMBER() OVER (PARTITION BY quote_currency ORDER BY rate DESC) AS rate_rank
  FROM fact_fx_rate
  WHERE base_currency = 'EUR'
)

SELECT
  rate_date,
  base_currency,
  quote_currency,
  rate
FROM ranked_rates
WHERE rate_rank = 1

-- Average rate of NOK-DKK per year
SELECT
  AVG(rate) AS average_rate,
  YEAR(rate_date)
FROM 
  fact_fx_rate
WHERE
  base_currency = 'NOK' AND quote_currency = 'DKK'
GROUP BY
  YEAR(rate_date)
ORDER BY average_rate DESC
  

-- Lowest rate of SEK-RON each month during 2022
SELECT
  MIN(rate) AS lowest_rate,
  date_trunc('month',rate_date) AS month
FROM 
  fact_fx_rate
WHERE
  base_currency = 'SEK' 
  AND quote_currency = 'RON'
  AND rate_date >= DATE '2022-01-01'
  AND rate_date < DATE '2023-01-01'
GROUP BY
  month
  
  
  