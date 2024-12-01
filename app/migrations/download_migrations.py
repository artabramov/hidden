DOWNLOAD_MIGRATIONS = [
    # The function that updates downloads_count for documents
    """
    CREATE OR REPLACE FUNCTION update_downloads_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE documents
            SET downloads_count = downloads_count + 1
            WHERE id = NEW.document_id;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE documents
            SET downloads_count = downloads_count - 1
            WHERE id = OLD.document_id;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # Drop the triggers if they already exist
    """
    DROP TRIGGER IF EXISTS after_insert_download ON documents_downloads;
    """,
    """
    DROP TRIGGER IF EXISTS after_delete_download ON documents_downloads;
    """,

    # Trigger for INSERT operation on downloads (to update downloads_count)
    """
    CREATE TRIGGER after_insert_download
    AFTER INSERT ON documents_downloads
    FOR EACH ROW
    EXECUTE FUNCTION update_downloads_count();
    """,

    # Trigger for DELETE operation on downloads (to update downloads_count)
    """
    CREATE TRIGGER after_delete_download
    AFTER DELETE ON documents_downloads
    FOR EACH ROW
    EXECUTE FUNCTION update_downloads_count();
    """,

    # Recount initial state
    """
    UPDATE documents
    SET downloads_count = (
        SELECT COUNT(*)
        FROM documents_downloads
        WHERE documents_downloads.document_id = documents.id
    );
    """
]
