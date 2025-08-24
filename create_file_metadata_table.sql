-- 创建文件信息表
CREATE TABLE IF NOT EXISTS file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    original_filename VARCHAR(255),
    file_size BIGINT,
    file_type VARCHAR(50),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    platform VARCHAR(50),
    file_path VARCHAR(500),
    processed_time TIMESTAMP NULL,
    record_count INT DEFAULT 0,
    status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_file_name ON file_metadata(file_name);
CREATE INDEX idx_upload_time ON file_metadata(upload_time);
CREATE INDEX idx_platform ON file_metadata(platform);
