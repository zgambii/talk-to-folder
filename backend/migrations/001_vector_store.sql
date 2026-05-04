create extension if not exists vector;

create table if not exists document_chunks (
    id text primary key,
    folder_id text not null,
    document_id text not null,
    drive_file_id text not null,
    document_name text not null,
    source_url text,
    chunk_index integer not null,
    text text not null,
    embedding vector(1536) not null,
    created_at timestamptz not null default now()
);

create index if not exists document_chunks_folder_id_idx
    on document_chunks (folder_id);

create index if not exists document_chunks_embedding_idx
    on document_chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

create or replace function match_document_chunks(
    query_embedding vector(1536),
    match_folder_id text,
    match_count integer default 8
)
returns table (
    id text,
    folder_id text,
    document_id text,
    drive_file_id text,
    document_name text,
    source_url text,
    chunk_index integer,
    text text,
    score double precision
)
language sql
stable
as $$
    select
        document_chunks.id,
        document_chunks.folder_id,
        document_chunks.document_id,
        document_chunks.drive_file_id,
        document_chunks.document_name,
        document_chunks.source_url,
        document_chunks.chunk_index,
        document_chunks.text,
        1 - (document_chunks.embedding <=> query_embedding) as score
    from document_chunks
    where document_chunks.folder_id = match_folder_id
    order by document_chunks.embedding <=> query_embedding
    limit match_count;
$$;
