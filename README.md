<div align="center">

<img src="https://cdn4.telesco.pe/file/HAgf-Yd0ybPzJ4s5e1xOpmRurxkqb8oRCqlJr72L-u8NTBNO5FYORKpupmh7KHDEm2QyntmLCtKJ1i6hJ3oiGy2rvw_Vk2-00E4z61SiVlef39_va0dRu58KX4qfo_oe3-Di2KsH8ZyD6DcZNxD8tPC6lzAYjchfj0dKA8CdqOX4fg8vvjhKwy8lh3p99mXhl6RZ5Lbcy52oQ2Vsq9ciNUSq_QQcSUOD2HCWWZtbO1yhM_kCmskpbCBLD2HY0oQ1j4_tXEqGYrCUb6rg7QlV2H00ocN5EKF3kvHlnp5Ex1AOzahk5ktvOmniZnw9FZG6mlVPF0lsWbfZRgYDjhniHg.jpg" alt="amd-bmi-bot" width="200" />

# dma-bmi-bot

Make your university life easier with this Telegram bot!

![version](https://img.shields.io/github/v/release/akimich11/dma-bmi-bot?color=success)
![contributors](https://img.shields.io/github/contributors/akimich11/dma-bmi-bot?style=flat-square)
![commits](https://img.shields.io/github/commit-activity/m/akimich11/dma-bmi-bot)
![total-lines](https://img.shields.io/tokei/lines/github/akimich11/dma-bmi-bot)

![issues-open](https://img.shields.io/github/issues/akimich11/dma-bmi-bot)
![issues-closed](https://img.shields.io/github/issues-closed/akimich11/dma-bmi-bot?color=success)
![pr-closed](https://img.shields.io/github/issues-pr-closed/akimich11/dma-bmi-bot?color=success)

![follow](https://img.shields.io/github/followers/akimich11?style=social)
</div>


# What can this bot do?

## Skip-tracking features
  - get skips of one user
  
    <img alt="skips" src="example_screenshots/skips.png" width="930"/>
  - get skips of all users
  
    <img alt="skips_all" src="example_screenshots/skips_all.png" width="930"/>
  - _(admin only)_ set skips of one user
  
    <img alt="set_skips" src="example_screenshots/set_skips.png" width="930"/>
  - _(admin only)_ increment skips for many users (by last names)
  
    <img alt="inc_skips" src="example_screenshots/inc_skips.png" width="930"/>
## Poll features
  - tag users who didn't vote
  
    <img alt="tag" src="example_screenshots/tag.png" width="930"/>
  - print poll stats (`/stats` command)
  
  - order voters by last name (built-in for all commands)
  
  - _(admin only)_ create polls 

    > just send poll to bot: it will create a copy of poll, send it to group chat and pin it
    <img alt="pin" src="example_screenshots/pin.png" width="930"/>
  - _(akim only)_ create schedule and send polls every week automatically

## Timetable features
  - print university timetable depending on department of user who made a request
  
    <img alt="timetable" src="example_screenshots/timetable.png" width="930"/>
## Greeting features
  - send congrats for user in his birthday
  
    <img alt="birthday" src="example_screenshots/birthday.png" width="930"/>
## Queue features
  - get queues list
  
    <img alt="queues" src="example_screenshots/queues.png" width="930"/>
  - get users list in queue
  
    <img alt="queue" src="example_screenshots/queue.png" width="930"/>
  - sign-up to queue
  
    <img alt="sign_up" src="example_screenshots/sign_up.png" width="930"/>
  - sign-up to particular place in queue (if it's free)
  
    <img alt="sign_up_place" src="example_screenshots/sign_up_place.png" width="930"/>
  - change position in queue
  
    <img alt="move" src="example_screenshots/move.png" width="930"/>
  - leave queue
  
    <img alt="cancel" src="example_screenshots/cancel.png" width="930"/>
  - leave queue and decrement queue positions
  
    <img alt="self_shift" src="example_screenshots/self_shift.png" width="930"/>
  - _(admin only)_ add queue
  
    <img alt="add_queue" src="example_screenshots/add_queue.png" width="930"/>
  - _(admin only)_ clear queue
  
    <img alt="clear_queue" src="example_screenshots/clear_queue.png" width="930"/>
  - _(admin only)_ remove queue
  
    <img alt="remove_queue" src="example_screenshots/remove_queue.png" width="930"/>
  - _(admin only)_ kick first user from queue and shift
  
    <img alt="shift_queue" src="example_screenshots/shift_queue.png" width="930"/>


# How to test the bot locally?
1. Install PostgreSQL: https://www.postgresql.org/download/.
2. Create user `postgres` with password `postgres` (to use other credentials, edit `settings.py`).
3. Create `dma_bmi_test` database with `public` schema in it.
4. Run the following script:

  ```sql
create sequence queue_id_seq
    as integer;

create sequence user_queue_id_seq
    as integer;

create sequence poll_option_id_seq
    as integer;

create sequence user_vote_id_seq
    as integer;

create table departments
(
    id      integer not null
        constraint department_pk
            primary key,
    chat_id integer,
    name    text


);


create table polls
(
    id            char(50) not null
        constraint poll_pk
            primary key,
    department_id integer
        constraint poll_department_id_fk
            references departments
            on update cascade on delete cascade,
    question      text,
    created_at    timestamp
);

create table users
(
    id             integer not null
        constraint user_pk
            primary key,

    first_name     text,
    last_name      varchar(20),
    department_id  integer
        constraint user_department_id_fk
            references departments
            on update cascade on delete cascade,
    sub_department char(3),
    is_admin       smallint,
    skips_month    integer,
    skips_semester integer,
    birthday       timestamp
);

create unique index user_last_name_uindex
    on users (last_name);

create table queues
(
    id            integer default nextval('queue_id_seq'::regclass) not null
        constraint queue_pk
            primary key,
    department_id integer
        constraint queue_department_id_fk
            references departments
            on update cascade on delete cascade,
    name          text,
    is_last       smallint
);

alter sequence queue_id_seq owned by queues.id;

create table scheduled_polls
(
    id            integer not null
        constraint poll_schedule_pk
            primary key,
    department_id integer
        constraint poll_schedule_department_id_fk
            references departments
            on update cascade on delete cascade,
    question      text,
    is_multi      smallint,
    weekday       char(9),
    utc_time      timestamp
);

create table poll_options
(
    id      integer default nextval('poll_option_id_seq'::regclass) not null
        constraint poll_option_pk
            primary key,
    poll_id char(50)
        constraint poll_option_poll_id_fk
            references polls
            on update cascade on delete cascade,
    text    text
);

alter sequence poll_option_id_seq owned by poll_options.id;

create table queue_positions
(
    id       integer default nextval('user_queue_id_seq'::regclass) not null
        constraint user_queue_pk
            primary key,
    user_id  integer
        constraint user_queue_user_id_fk
            references users
            on update cascade on delete cascade,
    queue_id integer
        constraint user_queue_queue_id_fk
            references queues
            on update cascade on delete cascade,
    position integer
);

alter sequence user_queue_id_seq owned by queue_positions.id;

create table users_poll_options
(
    id        integer default nextval('user_vote_id_seq'::regclass) not null
        constraint user_vote_pk
            primary key,
    user_id   integer
        constraint user_vote_user_id_fk
            references users
            on update cascade on delete cascade,
    option_id integer
        constraint user_vote_poll_option_id_fk
            references poll_options
            on update cascade on delete cascade
);

alter sequence user_vote_id_seq owned by users_poll_options.id;

create table timetables
(
    id             serial
        constraint timetables_pk
            primary key,
    department_id  integer
        constraint timetables_departments_id_fk
            references departments
            on update cascade on delete cascade,
    sub_department varchar(255) default NULL::character varying,
    weekday        varchar(255),
    start_time     time,
    subject        varchar(255),
    auditory       varchar(255),
    type           char
);
  ```

5. Fill database with some test data. 
> We recommend adding your Telegram id to `departments` table in `chat_id` field. 
This allows you to test all commands within your own bot chat.
6. Run the following command
  
  ```bash
  python __main__.py
  ```
  > By default, script uses https://t.me/famcs_timetable_bot for tests, 
but you can change bot token in `settings.py` and use your own bot. 
7. Press `start` in bot chat and enjoy!

