-- Insert template for Daily Digest (SQLite)
-- This file contains placeholders only. No actual data is inserted by default.
-- Usage:
-- 1) Open DB: sqlite3 newsapp.db
-- 2) Edit values below (replace angle-bracket placeholders)
-- 3) Run: .read insert_template.sql

PRAGMA foreign_keys = ON;

/*
   USERS
   - username and email must be unique
*/
-- INSERT INTO users (username, email, password, preferences, premium)
-- VALUES (
--     '<username>',
--     '<email@example.com>',
--     '<password>',
--     '<preferences_csv>',
--     <0_or_1>
-- );

/*
   ARTICLES
   - add one article row
   - recommended date format: YYYY-MM-DD
*/
-- INSERT INTO articles (title, author, content, category, date, tags, premium)
-- VALUES (
--     '<title>',
--     '<author_name>',
--     '<full_content>',
--     '<category>',
--     '<YYYY-MM-DD>',
--     '<tag1,tag2,tag3>',
--     <0_or_1>
-- );

/*
   COMMENTS
   - article_id and user_id must exist
   - recommended timestamp format: YYYY-MM-DD HH:MM
*/
-- INSERT INTO comments (article_id, user_id, content, timestamp)
-- VALUES (
--     <article_id>,
--     <user_id>,
--     '<comment_text>',
--     '<YYYY-MM-DD HH:MM>'
-- );

/*
   INTERACTIONS
   - type must be one of: View, Like, Bookmark, Share
   - UNIQUE(user_id, article_id, type) prevents exact duplicates
*/
-- INSERT OR IGNORE INTO interactions (user_id, article_id, type)
-- VALUES (
--     <user_id>,
--     <article_id>,
--     '<View_or_Like_or_Bookmark_or_Share>'
-- );

/*
   OPTIONAL: safer article insert pattern (prevents duplicate title+date)
   Replace placeholders before use.
*/
-- INSERT INTO articles (title, author, content, category, date, tags, premium)
-- SELECT
--     '<title>',
--     '<author_name>',
--     '<full_content>',
--     '<category>',
--     '<YYYY-MM-DD>',
--     '<tag1,tag2>',
--     <0_or_1>
-- WHERE NOT EXISTS (
--     SELECT 1
--     FROM articles
--     WHERE title = '<title>' AND date = '<YYYY-MM-DD>'
-- );