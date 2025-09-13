-- Наполнение тестовой БД
insert into channels (tg_channel_id, title) values (1234567890, 'Demo Channel');
insert into tags (channel_id, name) values (1, 'Новости'), (1, 'Аналитика');
insert into series (channel_id, code, title) values (1, 'weekly', 'Недельные заметки');
