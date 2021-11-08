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

INSERT INTO public.project
(id, name, owner, contributors)
VALUES
(gen_random_uuid(), 'test-project', 'jon', '{jon,jacob}');