COMMENT_MIGRATIONS = [
    # The function that updates comments_count for documents
    """
    CREATE OR REPLACE FUNCTION update_comments_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE documents
            SET comments_count = comments_count + 1
            WHERE id = NEW.document_id;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE documents
            SET comments_count = comments_count - 1
            WHERE id = OLD.document_id;
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """,

    # Drop the triggers if they already exist
    """
    DROP TRIGGER IF EXISTS after_insert_comment ON comments;
    """,
    """
    DROP TRIGGER IF EXISTS after_delete_comment ON comments;
    """,

    # Trigger for INSERT operation on comments (to update comments_count)
    """
    CREATE TRIGGER after_insert_comment
    AFTER INSERT ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_comments_count();
    """,

    # Trigger for DELETE operation on comments (to update comments_count)
    """
    CREATE TRIGGER after_delete_comment
    AFTER DELETE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_comments_count();
    """,

    # Recount initial state
    """
    UPDATE documents
    SET comments_count = (
        SELECT COUNT(*)
        FROM comments
        WHERE comments.document_id = documents.id
    );
    """
]
