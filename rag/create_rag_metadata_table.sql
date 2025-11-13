-- Create rag_index_metadata table for tracking indexing timestamps
-- This table stores metadata about RAG indexing operations

CREATE TABLE IF NOT EXISTS rag_index_metadata (
    id INT PRIMARY KEY AUTO_INCREMENT,
    last_indexed_at DATETIME NOT NULL COMMENT 'Timestamp of last indexing',
    indexed_hotels INT DEFAULT 0 COMMENT 'Number of hotels indexed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Record update time',
    INDEX idx_last_indexed (last_indexed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='RAG indexing metadata table';

-- Example: View latest indexing info
-- SELECT * FROM rag_index_metadata ORDER BY id DESC LIMIT 1;

