DROP SCHEMA dbo;

CREATE SCHEMA dbo;

CREATE TABLE alembic_version (
	version_num varchar(32) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE blog_posts (
	id int IDENTITY(1,1) NOT NULL,
	title varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	slug varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	excerpt varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	content varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	author varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	tags varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	image_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	published bit NOT NULL,
	views int NOT NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	updated_at datetimeoffset DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__blog_pos__3213E83FA76C64F1 PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX ix_blog_posts_id ON dbo.blog_posts (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE UNIQUE NONCLUSTERED INDEX ix_blog_posts_slug ON dbo.blog_posts (slug ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE contact_messages (
	id int IDENTITY(1,1) NOT NULL,
	name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	email varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	subject varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	message varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[read] bit NOT NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__contact___3213E83F9919DD5D PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX ix_contact_messages_id ON dbo.contact_messages (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE images (
	id int IDENTITY(1,1) NOT NULL,
	entity_id int NOT NULL,
	entity_type varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	image_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	image_order int NULL,
	alt_text nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetime2 DEFAULT getdate() NOT NULL,
	blob_name nvarchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	file_size int NULL,
	content_type nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	updated_at datetime2 DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__images__3213E83F06ED40D3 PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX IX_images_entity ON dbo.images (entity_id ASC, entity_type ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX IX_images_order ON dbo.images (entity_id ASC, entity_type ASC, image_order ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_images_entity_id ON dbo.images (entity_id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_images_entity_type ON dbo.images (entity_type ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_images_id ON dbo.images (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE login_attempts (
	id int IDENTITY(1,1) NOT NULL,
	email varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	ip_address varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	success bit NOT NULL,
	created_at datetime2 DEFAULT getutcdate() NOT NULL,
	CONSTRAINT PK__login_at__3213E83FB6816999 PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX ix_login_attempts_email ON dbo.login_attempts (email ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_login_attempts_id ON dbo.login_attempts (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE profiles (
	id int IDENTITY(1,1) NOT NULL,
	username varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	last_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	display_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	title varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	bio varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	email varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	github_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	linkedin_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	twitter_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	profile_image_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	skills varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	resume_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	updated_at datetimeoffset DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__profiles__3213E83F2861BA27 PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX ix_profiles_id ON dbo.profiles (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE UNIQUE NONCLUSTERED INDEX ix_profiles_username ON dbo.profiles (username ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE projects (
	id int IDENTITY(1,1) NOT NULL,
	title varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	description varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	content varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	technologies varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	github_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	demo_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	featured bit NOT NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	updated_at datetimeoffset DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__projects__3213E83FB7A7A281 PRIMARY KEY (id)
);
CREATE NONCLUSTERED INDEX ix_projects_id ON dbo.projects (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE reactions (
	id int IDENTITY(1,1) NOT NULL,
	email nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	name nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	reaction_type nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	entity_id int NOT NULL,
	entity_type nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	ip_address nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetime2 DEFAULT getdate() NOT NULL,
	updated_at datetime2 DEFAULT getdate() NOT NULL,
	CONSTRAINT PK__reaction__3213E83F75769DEA PRIMARY KEY (id),
	CONSTRAINT UQ_reaction_per_entity UNIQUE (email,entity_id,entity_type)
);
CREATE NONCLUSTERED INDEX IX_reactions_email ON dbo.reactions (email ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX IX_reactions_entity ON dbo.reactions (entity_id ASC, entity_type ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX IX_reactions_type ON dbo.reactions (entity_id ASC, entity_type ASC, reaction_type ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
ALTER TABLE dbo.reactions WITH NOCHECK ADD CONSTRAINT CK_reactions_type CHECK (([reaction_type]='congratulations' OR [reaction_type]='love' OR [reaction_type]='like'));
ALTER TABLE dbo.reactions WITH NOCHECK ADD CONSTRAINT CK_reactions_entity_type CHECK (([entity_type]='project' OR [entity_type]='blog_post'));

CREATE TABLE subscribers (
	id int IDENTITY(1,1) NOT NULL,
	email nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	is_active bit DEFAULT 1 NOT NULL,
	verification_token nvarchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	is_verified bit DEFAULT 0 NOT NULL,
	created_at datetimeoffset DEFAULT sysdatetimeoffset() NOT NULL,
	updated_at datetimeoffset DEFAULT sysdatetimeoffset() NOT NULL,
	CONSTRAINT PK__subscrib__3213E83F0DC1D2E1 PRIMARY KEY (id),
	CONSTRAINT UQ__subscrib__AB6E61645D3F9D4A UNIQUE (email)
);
CREATE NONCLUSTERED INDEX idx_subscribers_active ON dbo.subscribers (is_active ASC, is_verified ASC) 
	WHERE ([is_active]=(1) AND [is_verified]=(1))
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX idx_subscribers_email ON dbo.subscribers (email ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX idx_subscribers_token ON dbo.subscribers (verification_token ASC) 
	WHERE ([verification_token] IS NOT NULL)
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE users (
	id int IDENTITY(1,1) NOT NULL,
	email varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	username varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	hashed_password varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	full_name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	is_active bit DEFAULT 1 NOT NULL,
	is_superuser bit DEFAULT 0 NOT NULL,
	email_2fa_enabled bit DEFAULT 1 NOT NULL,
	totp_secret varchar(32) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	totp_enabled bit DEFAULT 0 NOT NULL,
	backup_codes text COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetime2 DEFAULT getutcdate() NOT NULL,
	updated_at datetime2 DEFAULT getutcdate() NOT NULL,
	last_login datetime2 NULL,
	CONSTRAINT PK__users__3213E83F93B863AE PRIMARY KEY (id),
	CONSTRAINT UQ__users__AB6E61644761539C UNIQUE (email),
	CONSTRAINT UQ__users__F3DBC572C482F414 UNIQUE (username)
);
CREATE NONCLUSTERED INDEX ix_users_email ON dbo.users (email ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_users_id ON dbo.users (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_users_username ON dbo.users (username ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE comments (
	id int IDENTITY(1,1) NOT NULL,
	name varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	email varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	content varchar(MAX) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	approved bit NOT NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	project_id int NULL,
	blog_post_id int NULL,
	CONSTRAINT PK__comments__3213E83F0912F23C PRIMARY KEY (id),
	CONSTRAINT FK__comments__blog_p__03F0984C FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
	CONSTRAINT FK__comments__projec__02FC7413 FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE NONCLUSTERED INDEX ix_comments_id ON dbo.comments (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE two_factor_codes (
	id int IDENTITY(1,1) NOT NULL,
	user_id int NOT NULL,
	code varchar(6) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	expires_at datetime2 NOT NULL,
	used bit DEFAULT 0 NOT NULL,
	created_at datetime2 DEFAULT getutcdate() NOT NULL,
	CONSTRAINT PK__two_fact__3213E83FA1C25AC4 PRIMARY KEY (id),
	CONSTRAINT FK__two_facto__user___17036CC0 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE NONCLUSTERED INDEX ix_two_factor_codes_id ON dbo.two_factor_codes (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];
CREATE NONCLUSTERED INDEX ix_two_factor_codes_user_id ON dbo.two_factor_codes (user_id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];

CREATE TABLE videos (
	id int IDENTITY(1,1) NOT NULL,
	title varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[source] varchar(12) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	thumbnail_url varchar(500) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	created_at datetimeoffset DEFAULT getdate() NOT NULL,
	project_id int NULL,
	blog_post_id int NULL,
	CONSTRAINT PK__videos__3213E83FEBC6F0EE PRIMARY KEY (id),
	CONSTRAINT FK__videos__blog_pos__08B54D69 FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
	CONSTRAINT FK__videos__project___07C12930 FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE NONCLUSTERED INDEX ix_videos_id ON dbo.videos (id ASC) 
	WITH (PAD_INDEX = OFF, FILLFACTOR = 100, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, STATISTICS_NORECOMPUTE = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY];