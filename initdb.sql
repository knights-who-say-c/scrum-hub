CREATE SEQUENCE public.tasks_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.tasks_id_seq
    OWNER TO postgres;

CREATE TABLE IF NOT EXISTS public.project
(
    id uuid NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    owner text COLLATE pg_catalog."default",
    contributors text[] COLLATE pg_catalog."default",
    CONSTRAINT project_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.project
    OWNER to postgres;

CREATE TABLE IF NOT EXISTS public.tasks
(
    type text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    label text COLLATE pg_catalog."default",
    assignee text COLLATE pg_catalog."default",
    duedate date,
    pipeline text COLLATE pg_catalog."default",
    id integer NOT NULL DEFAULT nextval('tasks_id_seq'::regclass),
    project text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.tasks
    OWNER to postgres;