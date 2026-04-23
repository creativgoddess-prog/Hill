-- Run this entire block in the Supabase SQL Editor
-- Dashboard → SQL Editor → New Query → paste this → Run

create table if not exists public.user_sessions (
  telegram_user_id  bigint primary key,
  interview_answers jsonb   default '{}'::jsonb,
  chosen_method     text    default '',
  top_methods       text    default '',
  recommendation    text    default '',
  plan              text    default '',
  brand             jsonb   default '{}'::jsonb,
  pain_points       jsonb   default '{}'::jsonb,
  build_niche       text    default '',
  build_service     text    default '',
  build_platforms   jsonb   default '[]'::jsonb,
  conversation_history jsonb default '[]'::jsonb,
  formatted_research   text  default '',
  updated_at        timestamptz default now()
);

-- Allow the bot full access using the anon key
alter table public.user_sessions enable row level security;

create policy "bot_full_access"
  on public.user_sessions
  for all
  using (true)
  with check (true);
