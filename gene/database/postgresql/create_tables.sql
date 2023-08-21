CREATE TABLE gene_sources (
    name VARCHAR(127) PRIMARY KEY,
    data_license TEXT NOT NULL,
    data_license_url TEXT NOT NULL,
    version TEXT NOT NULL,
    data_url JSON NOT NULL,
    rdp_url TEXT,
    data_license_nc BOOLEAN NOT NULL,
    data_license_attr BOOLEAN NOT NULL,
    data_license_sa BOOLEAN NOT NULL,
    genome_assemblies TEXT [] NOT NULL
);
-- see also: delete_normalized_concepts.sql
CREATE TABLE gene_merged (
    concept_id VARCHAR(127) PRIMARY KEY,
    symbol TEXT,
    symbol_status VARCHAR(127),
    previous_symbols TEXT [],
    label TEXT,
    strand VARCHAR(1),
    ensembl_locations JSON [],
    hgnc_locations JSON [],
    ncbi_locations JSON [],
    location_annotations TEXT [],
    ensembl_biotype TEXT [],
    hgnc_locus_type TEXT [],
    ncbi_gene_type TEXT [],
    aliases TEXT [],
    associated_with TEXT [],
    xrefs TEXT []
);
CREATE TABLE gene_concepts (
    concept_id VARCHAR(127) PRIMARY KEY,
    source VARCHAR(127) NOT NULL REFERENCES gene_sources (name),
    symbol_status VARCHAR(127),
    label TEXT,
    strand VARCHAR(1),
    location_annotations TEXT [],
    locations JSON [],
    gene_type TEXT,
    merge_ref VARCHAR(127) REFERENCES gene_merged (concept_id)
);
CREATE TABLE gene_symbols (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    concept_id VARCHAR(127) REFERENCES gene_concepts (concept_id)
);
CREATE TABLE gene_previous_symbols (
    id SERIAL PRIMARY KEY,
    prev_symbol TEXT NOT NULL,
    concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
);
CREATE TABLE gene_aliases (
    id SERIAL PRIMARY KEY,
    alias TEXT NOT NULL,
    concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
);
CREATE TABLE gene_xrefs (
    id SERIAL PRIMARY KEY,
    xref TEXT NOT NULL,
    concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
);
CREATE TABLE gene_associations (
    id SERIAL PRIMARY KEY,
    associated_with TEXT NOT NULL,
    concept_ID VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
);
