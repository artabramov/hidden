REVISION_MIGRATIONS = [
    # The function that updates revisions_count for documents
    """
    CREATE OR REPLACE FUNCTION update_revisions_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE documents
            SET revisions_count = revisions_count + 1
            WHERE id = NEW.document_id;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE documents
            SET revisions_count = revisions_count - 1
            WHERE id = OLD.document_id;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # Drop the triggers if they already exist
    """
    DROP TRIGGER IF EXISTS after_insert_revision ON documents_revisions;
    """,
    """
    DROP TRIGGER IF EXISTS after_delete_revision ON documents_revisions;
    """,

    # Trigger for INSERT operation on revisions (to update revisions_count)
    """
    CREATE TRIGGER after_insert_revision
    AFTER INSERT ON documents_revisions
    FOR EACH ROW
    EXECUTE FUNCTION update_revisions_count();
    """,

    # Trigger for DELETE operation on revisions (to update revisions_count)
    """
    CREATE TRIGGER after_delete_revision
    AFTER DELETE ON documents_revisions
    FOR EACH ROW
    EXECUTE FUNCTION update_revisions_count();
    """,

    # Recount initial state
    """
    UPDATE documents
    SET revisions_count = (
        SELECT COUNT(*)
        FROM documents_revisions
        WHERE documents_revisions.document_id = documents.id
    );
    """
]
