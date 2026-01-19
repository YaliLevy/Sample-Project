-- WhatsApp Real Estate Bot - Supabase Database Setup
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard → SQL Editor → New Query

-- ===================================
-- 1. PROPERTIES TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,

    -- Property details
    property_type VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL DEFAULT 'תל אביב',
    street VARCHAR(200),
    street_number VARCHAR(20),
    address VARCHAR(500),

    rooms DECIMAL(3,1),  -- 2.5, 3.5, etc.
    size INTEGER,  -- Square meters
    floor INTEGER,
    price INTEGER NOT NULL,  -- In ILS

    transaction_type VARCHAR(20) NOT NULL,  -- 'rent' or 'sale'

    -- Owner information
    owner_name VARCHAR(200),
    owner_phone VARCHAR(20),

    description TEXT,

    -- Status tracking
    status VARCHAR(20) DEFAULT 'available',  -- available, rented, sold, pending

    -- Metadata
    phone_number VARCHAR(20) NOT NULL,  -- Who added this property
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for properties
CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_rooms ON properties(rooms);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_transaction_type ON properties(transaction_type);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);

-- ===================================
-- 2. CLIENTS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,

    -- Client information
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),

    -- Search criteria
    looking_for VARCHAR(20) NOT NULL,  -- 'rent' or 'buy'
    property_type VARCHAR(50),
    city VARCHAR(100),

    min_rooms DECIMAL(3,1),
    max_rooms DECIMAL(3,1),
    min_price INTEGER,
    max_price INTEGER,
    min_size INTEGER,  -- Minimum square meters

    preferred_areas TEXT,  -- JSON array of area names
    notes TEXT,

    -- Status tracking
    status VARCHAR(20) DEFAULT 'active',  -- active, closed, pending

    -- Metadata
    phone_number VARCHAR(20) NOT NULL,  -- Who added this client
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for clients
CREATE INDEX IF NOT EXISTS idx_clients_looking_for ON clients(looking_for);
CREATE INDEX IF NOT EXISTS idx_clients_city ON clients(city);
CREATE INDEX IF NOT EXISTS idx_clients_min_price ON clients(min_price);
CREATE INDEX IF NOT EXISTS idx_clients_max_price ON clients(max_price);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);

-- ===================================
-- 3. PHOTOS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,

    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- Photo storage (Supabase Storage URLs)
    file_path VARCHAR(500) NOT NULL,
    twilio_media_url VARCHAR(500),
    media_content_type VARCHAR(50),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for photos
CREATE INDEX IF NOT EXISTS idx_photos_property_id ON photos(property_id);

-- ===================================
-- 4. MATCHES TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,

    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,

    score DECIMAL(5,2) NOT NULL,  -- Match quality 0-100

    -- Status tracking
    status VARCHAR(20) DEFAULT 'suggested',  -- suggested, sent, interested, rejected, closed

    -- Metadata
    suggested_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for matches
CREATE INDEX IF NOT EXISTS idx_matches_property_id ON matches(property_id);
CREATE INDEX IF NOT EXISTS idx_matches_client_id ON matches(client_id);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);

-- ===================================
-- 5. CONVERSATIONS TABLE
-- ===================================
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,

    phone_number VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,

    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_phone_number ON conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);

-- ===================================
-- TRIGGERS FOR UPDATED_AT
-- ===================================

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to properties
DROP TRIGGER IF EXISTS update_properties_updated_at ON properties;
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to clients
DROP TRIGGER IF EXISTS update_clients_updated_at ON clients;
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to matches
DROP TRIGGER IF EXISTS update_matches_updated_at ON matches;
CREATE TRIGGER update_matches_updated_at
    BEFORE UPDATE ON matches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================
-- VERIFICATION
-- ===================================
-- Check that all tables were created successfully
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND table_name IN ('properties', 'clients', 'photos', 'matches', 'conversations')
ORDER BY table_name;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database setup complete!';
    RAISE NOTICE 'Tables created: properties, clients, photos, matches, conversations';
    RAISE NOTICE 'All indexes and triggers configured successfully.';
END $$;
