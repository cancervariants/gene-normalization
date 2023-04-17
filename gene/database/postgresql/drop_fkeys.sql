ALTER TABLE gene_aliases DROP CONSTRAINT gene_aliases_concept_id_fkey;
ALTER TABLE gene_associations DROP CONSTRAINT gene_associations_concept_id_fkey;
ALTER TABLE gene_previous_symbols
    DROP CONSTRAINT gene_previous_symbols_concept_id_fkey;
ALTER TABLE gene_symbols DROP CONSTRAINT gene_symbols_concept_id_fkey;
ALTER TABLE gene_xrefs DROP CONSTRAINT gene_xrefs_concept_id_fkey;
