-- deploy/schema.sql — базовая схема ControllerBot-лайт 2.0

create table if not exists channels (
  id bigserial primary key,
  tg_channel_id bigint unique not null,
  title text,
  timezone text default 'Europe/Moscow',
  created_at timestamptz default now()
);

create table if not exists series (
  id bigserial primary key,
  channel_id bigint not null references channels(id) on delete cascade,
  code text not null,
  title text,
  next_number int default 1,
  created_at timestamptz default now(),
  unique(channel_id, code)
);

do $$ begin
  create type post_status as enum ('draft','scheduled','published','deleted');
exception
  when duplicate_object then null;
end $$;

create table if not exists posts (
  id bigserial primary key,
  channel_id bigint not null references channels(id) on delete cascade,
  user_id bigint not null,
  title text,
  body_md text not null,
  status post_status default 'draft',
  scheduled_at timestamptz,
  published_at timestamptz,
  message_id bigint,
  series_id bigint references series(id) on delete set null,
  tags_cache text[],
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists tags (
  id bigserial primary key,
  channel_id bigint not null references channels(id) on delete cascade,
  name text not null,
  kind text default 'regular',
  unique(channel_id, name)
);

create table if not exists post_tags (
  post_id bigint not null references posts(id) on delete cascade,
  tag_id  bigint not null references tags(id) on delete cascade,
  primary key (post_id, tag_id)
);

create table if not exists reminders (
  id bigserial primary key,
  channel_id bigint not null references channels(id) on delete cascade,
  kind text not null,
  schedule_cron text,
  enabled boolean default true,
  created_at timestamptz default now()
);

create table if not exists digests (
  id bigserial primary key,
  channel_id bigint not null references channels(id) on delete cascade,
  period_start date not null,
  period_end date not null,
  kind text not null,
  status text default 'scheduled',
  export_path text,
  created_at timestamptz default now()
);

create index if not exists idx_posts_sched on posts (status, scheduled_at);
create index if not exists idx_posts_channel_created on posts (channel_id, created_at desc);
