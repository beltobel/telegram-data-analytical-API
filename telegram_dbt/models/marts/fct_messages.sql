select
    msg.id as message_id,
    msg.channel as channel_id,
    date_trunc('day', msg.message_date) as date_id,
    msg.message,
    msg.sender_id,
    case when msg.downloaded_image_path is not null then true else false end as has_image,
    length(msg.message) as message_length
from {{ ref('stg_telegram_messages') }} msg
