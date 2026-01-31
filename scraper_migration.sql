INSERT INTO audioV2
(db_id, account_name, content_id, audio_asset_id, original_audio_title, ig_artist_username, ig_artist_id)

SELECT 
a.db_id ,
p.account_name,
a.content_id,
audio_asset_id, 
original_audio_title, 
ig_artist_username, 
ig_artist_id
FROM audio a left join posts p on p.content_id = a.content_id 

INSERT INTO hashtagsV2
(db_id, account_name, content_id, hashtag)
SELECT 
db_id, 
p.account_name ,
h.content_id, 
hashtag
FROM hashtags h left join posts p on p.content_id = h.content_id 

INSERT INTO post_contentV2
(db_id, account_name, content_id, "index", "type", url, id, alt_text)

SELECT db_id,p.account_name ,pc.content_id, "index", "type", pc.url, pc.id, pc.alt_text
FROM post_content pc left join posts p on pc.content_id  = p.content_id 

INSERT INTO tagged_usersV2
(db_id, account_name, content_id, full_name, id, is_verified, profile_pic_url, username)
SELECT db_id,p.account_name , t.content_id, t.full_name, t.id, t.is_verified, t.profile_pic_url, t.username
FROM tagged_users t left join posts p on p.content_id = t.content_id 