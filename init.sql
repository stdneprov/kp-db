CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    need_reset_password BOOLEAN DEFAULT false
);

CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    games_count INT DEFAULT 0
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    games_count INT DEFAULT 0
);

CREATE TABLE consoles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    games_count INT DEFAULT 0,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    console_id INT,
    FOREIGN KEY (console_id) REFERENCES consoles(id) ON DELETE CASCADE,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    genre_id INT,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

-- Функцмя обновления games_count компании
CREATE OR REPLACE FUNCTION update_company_games_count()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN
        UPDATE companies
        SET games_count = games_count + 1
        WHERE id = NEW.company_id;
    END IF;

    IF TG_OP = 'DELETE' THEN
        UPDATE companies
        SET games_count = games_count - 1
        WHERE id = OLD.company_id;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.company_id IS DISTINCT FROM NEW.company_id THEN
            -- Уменьшаем счетчик у старой компании
            UPDATE companies
            SET games_count = games_count - 1
            WHERE id = OLD.company_id;

            -- Увеличиваем счетчик у новой компании
            UPDATE companies
            SET games_count = games_count + 1
            WHERE id = NEW.company_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_company_games_count
AFTER INSERT OR DELETE OR UPDATE OF company_id
ON games
FOR EACH ROW
EXECUTE FUNCTION update_company_games_count();

-- Функцмя обновления games_count консоли
CREATE OR REPLACE FUNCTION update_console_games_count()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN
        UPDATE consoles
        SET games_count = games_count + 1
        WHERE id = NEW.console_id;
    END IF;

    IF TG_OP = 'DELETE' THEN
        UPDATE consoles
        SET games_count = games_count - 1
        WHERE id = OLD.console_id;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.console_id IS DISTINCT FROM NEW.console_id THEN
            -- Уменьшаем счетчик у старой компании
            UPDATE consoles
            SET games_count = games_count - 1
            WHERE id = OLD.console_id;

            -- Увеличиваем счетчик у новой компании
            UPDATE consoles
            SET games_count = games_count + 1
            WHERE id = NEW.console_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_console_games_count
AFTER INSERT OR DELETE OR UPDATE OF console_id
ON games
FOR EACH ROW
EXECUTE FUNCTION update_console_games_count();

CREATE OR REPLACE FUNCTION update_genre_games_count()
RETURNS TRIGGER AS $$
BEGIN

    IF TG_OP = 'INSERT' THEN
        UPDATE genres
        SET games_count = games_count + 1
        WHERE id = NEW.genre_id;
    END IF;

    IF TG_OP = 'DELETE' THEN
        UPDATE genres
        SET games_count = games_count - 1
        WHERE id = OLD.genre_id;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.genre_id IS DISTINCT FROM NEW.genre_id THEN
            -- Уменьшаем счетчик у старой компании
            UPDATE genres
            SET games_count = games_count - 1
            WHERE id = OLD.genre_id;

            -- Увеличиваем счетчик у новой компании
            UPDATE genres
            SET games_count = games_count + 1
            WHERE id = NEW.genre_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_genre_games_count
AFTER INSERT OR DELETE OR UPDATE OF genre_id
ON games
FOR EACH ROW
EXECUTE FUNCTION update_genre_games_count();

CREATE OR REPLACE FUNCTION validate_user_role()
RETURNS TRIGGER AS $$
BEGIN
    -- Устанавливаем допустимые роли
    IF NOT (NEW.role IN ('admin', 'super_admin', 'user')) THEN
        RAISE EXCEPTION 'Invalid role: %. Allowed roles are admin, super_admin, user.', NEW.role;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_user_role
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION validate_user_role();

CREATE VIEW games_full_info AS
SELECT 
    g.id AS id,
    g.title AS title,
    g.description AS description,
    c.title AS company,
    gen.title AS genre,
    con.title AS console
FROM 
    games g
LEFT JOIN companies c ON g.company_id = c.id
LEFT JOIN genres gen ON g.genre_id = gen.id
LEFT JOIN consoles con ON c.id = con.company_id;

CREATE VIEW consoles_full_info AS
SELECT 
    con.id AS id,
    con.title AS title,
    con.description AS description,
    c.title AS company,
    con.games_count AS games_count
FROM 
    consoles con
LEFT JOIN companies c ON con.company_id = c.id;

INSERT INTO users (username, role, password_hash, need_reset_password)
VALUES ('root', 'super_admin', '', TRUE)
ON CONFLICT (username) DO NOTHING;
