USER_ROLE_MIGRATION = """
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN 
            CREATE TYPE userrole AS ENUM ('reader', 'writer', 'editor', 'admin'); 
        END IF; 
    END $$;
"""
