ALTER TABLE gene_aliases ADD CONSTRAINT gene_aliases_concept_id_fkey
    FOREIGN KEY (concept_id) REFERENCES gene_concepts (concept_id);
ALTER TABLE gene_associations ADD CONSTRAINT gene_associations_concept_id_fkey
    FOREIGN KEY (concept_id) REFERENCES gene_concepts (concept_id);
ALTER TABLE gene_previous_symbols
    ADD CONSTRAINT gene_previous_symbols_concept_id_fkey
    FOREIGN KEY (concept_id) REFERENCES gene_concepts (concept_id);
ALTER TABLE gene_symbols ADD CONSTRAINT gene_symbols_concept_id_fkey
    FOREIGN KEY (concept_id) REFERENCES gene_concepts (concept_id);
ALTER TABLE gene_xrefs ADD CONSTRAINT gene_xrefs_concept_id_fkey
    FOREIGN KEY (concept_id) REFERENCES gene_concepts (concept_id);
