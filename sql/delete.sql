DELETE FROM {{ table_name }}
    WHERE name=:name AND user=:user AND chat=:chat;
