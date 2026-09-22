CREATE TABLE scrape_results (
	id SERIAL PRIMARY KEY,
	url VARCHAR NOT NULL,
	requested_max_item INTEGER NOT NULL,
	collected INTEGER NOT NULL,
	post_urls TEXT NOT NULL,
	status VARCHAR NOT NULL,
	webhook_endpoint VARCHAR NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
