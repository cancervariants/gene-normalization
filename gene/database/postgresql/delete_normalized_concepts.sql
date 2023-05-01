-- some redundancy between here and create_tables.sql, drop_indexes.sql,
-- add_indexes.sql.
DROP INDEX IF EXISTS idx_gm_concept_id_low;
ALTER TABLE gene_concepts DROP CONSTRAINT IF EXISTS gene_concepts_merge_ref_fkey;
UPDATE gene_concepts SET merge_ref = NULL;
DROP TABLE gene_merged;
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
ALTER TABLE gene_concepts ADD CONSTRAINT gene_concepts_merge_ref_fkey
    FOREIGN KEY (merge_ref) REFERENCES gene_merged (concept_id);
CREATE INDEX idx_gm_concept_id_low
    ON gene_merged (lower(concept_id));
