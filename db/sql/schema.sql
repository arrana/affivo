DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_title VARCHAR(255) DEFAULT NULL,
    user_first_name VARCHAR(30) NOT NULL,
    user_middle_name VARCHAR(20) DEFAULT NULL,
    user_last_name VARCHAR(30) NOT NULL,
    user_passwd VARCHAR(255) NOT NULL,
    user_enabled TINYINT(1) DEFAULT 0,
    user_email VARCHAR(255) NOT NULL UNIQUE,
    user_login_attempts TINYINT(4) DEFAULT 0,
    user_account_locked TINYINT(4) DEFAULT 0,
    user_phone NUMERIC(10) NOT NULL,
    user_type ENUM('ADMIN', 'CUSTOMER') DEFAULT 'ADMIN',
    user_last_login DATETIME DEFAULT NULL,
    user_reset_pwd_token VARCHAR(32) DEFAULT NULL,
    user_email_verified ENUM('YES', 'NO') DEFAULT 'NO'
)  ENGINE=INNODB;