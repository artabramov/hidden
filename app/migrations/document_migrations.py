DOCUMENT_MIGRATIONS = [
    # The function that updates documents_count
    """
    CREATE OR REPLACE FUNCTION update_documents_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE collections
            SET documents_count = documents_count + 1
            WHERE id = NEW.collection_id;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE collections
            SET documents_count = documents_count - 1
            WHERE id = OLD.collection_id;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # Drop the triggers if they already exist
    """
    DROP TRIGGER IF EXISTS after_insert_document ON documents;
    """,
    """
    DROP TRIGGER IF EXISTS after_delete_document ON documents;
    """,

    # Trigger for INSERT operation
    """
    CREATE TRIGGER after_insert_document
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_count();
    """,

    # Trigger for DELETE operation
    """
    CREATE TRIGGER after_delete_document
    AFTER DELETE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_count();
    """,

    # Recount initial state
    """
    UPDATE collections
    SET documents_count = (
        SELECT COUNT(*)
        FROM documents
        WHERE documents.collection_id = collections.id
    );
    """
]
