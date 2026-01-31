
CREATE TABLE postsV2 (
	account_name VARCHAR NOT NULL,
	content_id VARCHAR NOT NULL, 
	account_url VARCHAR, 
	date_scraped VARCHAR NOT NULL, 
	url VARCHAR, 
	user_posted VARCHAR, 
	description VARCHAR, 
	num_comments INTEGER, 
	date_posted VARCHAR, 
	likes INTEGER, 
	photos TEXT, 
	videos TEXT, 
	location TEXT, 
	latest_comments TEXT, 
	post_id VARCHAR, 
	discovery_input VARCHAR, 
	has_handshake BOOLEAN, 
	shortcode VARCHAR, 
	content_type VARCHAR, 
	pk VARCHAR, 
	engagement_score_view INTEGER, 
	thumbnail VARCHAR, 
	video_view_count VARCHAR, 
	product_type VARCHAR, 
	coauthor_producers TEXT, 
	video_play_count INTEGER, 
	followers INTEGER, 
	posts_count INTEGER, 
	profile_image_link VARCHAR, 
	is_verified BOOLEAN, 
	is_paid_partnership BOOLEAN, 
	partnership_details TEXT, 
	user_posted_id VARCHAR, 
	profile_url VARCHAR, 
	videos_duration TEXT, 
	images TEXT, 
	alt_text VARCHAR, 
	photos_number INTEGER, 
	PRIMARY KEY (account_name,content_id)
);

CREATE TABLE hashtagsV2 (
    db_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL,
    content_id TEXT NOT NULL,
    hashtag TEXT NOT NULL,
    FOREIGN KEY (account_name, content_id)
        REFERENCES postsV2 (account_name, content_id)
        ON DELETE CASCADE
);

CREATE TABLE audioV2 (
	db_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	account_name TEXT NOT NULL,
	content_id VARCHAR NOT NULL,
	audio_asset_id VARCHAR, 
	original_audio_title VARCHAR, 
	ig_artist_username VARCHAR, 
	ig_artist_id VARCHAR, 
	FOREIGN KEY (account_name, content_id)
        REFERENCES postsV2 (account_name, content_id)
        ON DELETE CASCADE
);

CREATE TABLE post_contentV2 (
	db_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	account_name TEXT NOT NULL,
	content_id VARCHAR NOT NULL, 
	"index" INTEGER, 
	type VARCHAR, 
	url VARCHAR, 
	id VARCHAR, 
	alt_text VARCHAR, 
	FOREIGN KEY (account_name, content_id)
        REFERENCES postsV2 (account_name, content_id)
        ON DELETE CASCADE
);


CREATE TABLE tagged_usersV2 (
	db_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	account_name TEXT NOT NULL,
	content_id VARCHAR NOT NULL, 
	full_name VARCHAR, 
	id INTEGER, 
	is_verified BOOLEAN, 
	profile_pic_url VARCHAR, 
	username VARCHAR, 
	FOREIGN KEY (account_name, content_id)
        REFERENCES postsV2 (account_name, content_id)
        ON DELETE CASCADE
)