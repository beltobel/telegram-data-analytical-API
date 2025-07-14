select distinct
    date_trunc('day', message_date) as date_id,
    extract(day from message_date) as day,
    extract(month from message_date) as month,
    extract(year from message_date) as year,
    to_char(message_date, 'Day') as day_name
from {{ ref('stg_telegram_messages') }}
