-- Forte Membership — Supabase PostgreSQL schema
-- Run once in Supabase Dashboard → SQL Editor

CREATE TABLE IF NOT EXISTS members (
    member_id       VARCHAR(36) PRIMARY KEY,
    line_user_id    VARCHAR(64) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(32) NOT NULL UNIQUE,
    email           VARCHAR(255) DEFAULT '',
    gender          VARCHAR(16) DEFAULT '',
    birth_date      DATE,
    first_hotel     VARCHAR(100) DEFAULT '',
    registered_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS ix_members_line_user_id ON members(line_user_id);
CREATE INDEX IF NOT EXISTS ix_members_phone ON members(phone);
CREATE INDEX IF NOT EXISTS ix_members_status ON members(status);

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id         VARCHAR(64) PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    campaign_type       VARCHAR(32) NOT NULL DEFAULT 'custom',
    hotels              TEXT DEFAULT '',
    start_date          DATE,
    end_date            DATE,
    reward_type         VARCHAR(32) NOT NULL DEFAULT 'physical',
    reward_description  TEXT DEFAULT '',
    max_per_member      INTEGER NOT NULL DEFAULT 1,
    redeem_note         TEXT DEFAULT '',
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS ix_campaigns_status ON campaigns(status);

CREATE TABLE IF NOT EXISTS redemptions (
    redemption_id   VARCHAR(36) PRIMARY KEY,
    member_id       VARCHAR(36) NOT NULL,
    campaign_id     VARCHAR(64) NOT NULL,
    hotel           VARCHAR(100) NOT NULL,
    redeemed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    staff_id        VARCHAR(64) DEFAULT '',
    social_platform VARCHAR(32) DEFAULT '',
    note            TEXT DEFAULT '',
    reward_type     VARCHAR(32) DEFAULT 'physical',
    coupon_code     VARCHAR(64) DEFAULT '',
    status          VARCHAR(20) NOT NULL DEFAULT 'completed',
    CONSTRAINT uq_redemption_member_campaign UNIQUE (member_id, campaign_id)
);

CREATE INDEX IF NOT EXISTS ix_redemptions_member ON redemptions(member_id);

CREATE TABLE IF NOT EXISTS coupons (
    coupon_code   VARCHAR(64) PRIMARY KEY,
    campaign_id   VARCHAR(64) NOT NULL,
    member_id     VARCHAR(36),
    assigned_at   TIMESTAMPTZ,
    status        VARCHAR(20) NOT NULL DEFAULT 'unused',
    expires_at    DATE
);

CREATE INDEX IF NOT EXISTS ix_coupons_campaign_status ON coupons(campaign_id, status);

-- Seed: Stay Active 2026
INSERT INTO campaigns (
    campaign_id, name, campaign_type, hotels,
    start_date, end_date, reward_type, reward_description,
    max_per_member, redeem_note, status
) VALUES (
    'SA-2026-H1',
    'Stay Active 帥！先行動',
    'stay_active',
    '汐止福泰大飯店,福泰翡翠灣渡假飯店,彰化福泰商務飯店',
    '2026-01-01',
    '2026-12-31',
    'both',
    '精美禮品',
    1,
    '完成 Strava 路線 + 社群打卡後至櫃台兌換',
    'active'
) ON CONFLICT (campaign_id) DO NOTHING;
