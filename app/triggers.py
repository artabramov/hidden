triggers = [
    """
    CREATE OR REPLACE FUNCTION update_documents_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE collections
            SET documents_count = documents_count + 1
            WHERE id = NEW.collection_id;

        ELSIF (TG_OP = 'UPDATE') THEN
            UPDATE collections
            SET documents_count = (
                SELECT COUNT(*)
                FROM documents
                WHERE documents.collection_id = collections.id
            )
            WHERE id IN (OLD.collection_id, NEW.collection_id);

        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE collections
            SET documents_count = documents_count - 1
            WHERE id = OLD.collection_id;

        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """,

    "DROP TRIGGER IF EXISTS after_insert_document ON documents;",
    "DROP TRIGGER IF EXISTS after_update_document ON documents;",
    "DROP TRIGGER IF EXISTS after_delete_document ON documents;",

    """
    CREATE TRIGGER after_insert_document
    AFTER INSERT ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_count();
    """,

    """
    CREATE TRIGGER after_update_document
    AFTER UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_count();
    """,

    """
    CREATE TRIGGER after_delete_document
    AFTER DELETE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_documents_count();
    """,

    """
    UPDATE collections
    SET documents_count = (
        SELECT COUNT(*)
        FROM documents
        WHERE documents.collection_id = collections.id
    );
    """
]
