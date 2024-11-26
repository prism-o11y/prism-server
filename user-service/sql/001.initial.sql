-- Create Prism database
CREATE DATABASE prism;

-- Create status_types table
CREATE TABLE status_types (
  id SERIAL PRIMARY KEY,        -- Auto-incrementing ID for each status
  status VARCHAR(50) NOT NULL   -- Status name
);

-- Insert initial status values (active, removed, pending)
INSERT INTO status_types (status) VALUES ('active'), ('removed'), ('pending');

-- Create organizations table
CREATE TABLE organizations (
  org_id UUID PRIMARY KEY,        -- Manually generated UUID
  name VARCHAR(255) NOT NULL UNIQUE,  -- Organization name should be unique
  status_id INT NOT NULL REFERENCES status_types(id),  -- Foreign key to status_types
  created_at TIMESTAMPTZ NOT NULL,  -- Manually generated, using UTC timestamps
  updated_at TIMESTAMPTZ NOT NULL   -- Manually generated, using UTC timestamps
);

CREATE INDEX idx_org_name ON organizations (name);

-- Now create users table
CREATE TABLE users (
  user_id UUID PRIMARY KEY,         -- Application generated UUID
  org_id UUID NOT NULL,             -- Foreign key to organizations table
  email VARCHAR(255) NOT NULL UNIQUE,      -- Consider a unique constraint if required
  status_id INT NOT NULL REFERENCES status_types(id),  -- Foreign key to status_types
  created_at TIMESTAMPTZ NOT NULL,  -- Manually generated, using UTC timestamps
  updated_at TIMESTAMPTZ NOT NULL,  -- Manually generated, using UTC timestamps
  last_login TIMESTAMPTZ,           -- Last login timestamp

  -- Foreign key constraint with a unique name
  CONSTRAINT fk_users_org FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_org ON users (org_id);

-- Now create applications table
CREATE TABLE applications (
  app_id UUID PRIMARY KEY,          -- Manually generated UUID
  org_id UUID NOT NULL,             -- Foreign key to organizations table
  app_name VARCHAR(255) NOT NULL,
  app_url VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,  -- Manually generated, using UTC timestamps
  updated_at TIMESTAMPTZ NOT NULL,  -- Manually generated, using UTC timestamps

  -- Foreign key constraint with a unique name
  CONSTRAINT fk_applications_org FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX idx_app_name ON applications (app_name);
CREATE INDEX idx_org_app ON applications (org_id, app_name);
