CREATE INDEX idx_g_concept_id_low
    ON gene_concepts (lower(concept_id));
-- see also: delete_normalized_concepts.sql
CREATE INDEX idx_gm_concept_id_low ON gene_merged (lower(concept_id));
CREATE INDEX idx_gs_symbol_low ON gene_symbols (lower(symbol));
CREATE INDEX idx_gps_symbol_low
    ON gene_previous_symbols (lower(prev_symbol));
CREATE INDEX idx_ga_alias_low ON gene_aliases (lower(alias));
CREATE INDEX idx_gx_xref_low ON gene_xrefs (lower(xref));
CREATE INDEX idx_g_as_association_low
    ON gene_associations (lower(associated_with));
CREATE INDEX idx_rlv_concept_id_low
    ON record_lookup_view (lower(concept_id));
