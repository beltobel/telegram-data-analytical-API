-- models/staging/stg_telegram_messages.sql

with raw as (
    select * from raw_telegram_messages
),

cleaned as (
    select
        id,
        channel,
        message,
        downloaded_image_path,
        sender_id,
        date::timestamp as message_date
    from raw
)

select * from cleaned
