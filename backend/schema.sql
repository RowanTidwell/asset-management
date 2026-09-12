-- PostgreSQL schema for production-tracking MVP

-- Enable uuid generation (run once in DB)
-- CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- 'user' | 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE statuses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    type TEXT,
    status_id UUID REFERENCES statuses(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_assets_project_id ON assets(project_id);
CREATE INDEX idx_assets_name ON assets USING gin (to_tsvector('english', name));

CREATE TABLE shots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    sequence TEXT,
    start_frame INTEGER,
    end_frame INTEGER,
    status_id UUID REFERENCES statuses(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_shots_project_id ON shots(project_id);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('asset','shot')),
    entity_id UUID NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status_id UUID REFERENCES statuses(id),
    due_date DATE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    -- Simple FK integrity must be enforced at application level for polymorphic entity_id
    UNIQUE(entity_type, entity_id, name)
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);

CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('asset','shot','task','project')),
    entity_id UUID NOT NULL,
    body TEXT NOT NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Simple audit trigger example to update updated_at timestamps (can be wired in migrations)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER users_update_ts BEFORE UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER projects_update_ts BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER assets_update_ts BEFORE UPDATE ON assets
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER shots_update_ts BEFORE UPDATE ON shots
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER tasks_update_ts BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- End of schema
