-- Issue #104: make the official scoreline the standings and general scoring
-- contract while keeping event rows for explicitly timeline-led analysis.
-- Buhimba source record captured on 16 July 2026:
-- https://upl.co.ug/season/2025-26/
-- Durable audit context: https://github.com/humphrey-nyanzi/upl-lens/issues/104
-- The official URL later changed content, so the dated Issue evidence is part
-- of the provenance for the three-point deduction retained below.

-- Reconcile one known source-shaped minute typo in staging only. July 2026
-- hosted artifacts recorded Geofrey Gagganga's SC Villa goal in match 31655
-- as minute 334. A May snapshot, its paired assist, the complete five-goal
-- timeline, and the 1-4 scoreline support minute 34. raw.events remains the
-- immutable source record. The guard accepts exactly one malformed row or one
-- already-corrected row and fails closed for missing, duplicate, or unexpected
-- state; no other minute-334 event can match this natural key.
DO $$
DECLARE
    known_row_count INTEGER;
    malformed_row_count INTEGER;
    corrected_row_count INTEGER;
BEGIN
    SELECT
        COUNT(*),
        COUNT(*) FILTER (
            WHERE event_minute_text = '334'
                AND minute_base = 334
                AND minute_added = 0
                AND minute_total = 334
                AND is_added_time IS FALSE
                AND minute_period = '90+'
        ),
        COUNT(*) FILTER (
            WHERE event_minute_text = '34'
                AND minute_base = 34
                AND minute_added = 0
                AND minute_total = 34
                AND is_added_time IS FALSE
                AND minute_period = '31-45'
        )
    INTO known_row_count, malformed_row_count, corrected_row_count
    FROM staging.events
    WHERE season = '2025_26'
        AND match_id = 31655
        AND match_url = 'https://upl.co.ug/event/nec-fc-vs-sc-villa-3/'
        AND event_type = 'goal'
        AND team_name = 'SC Villa'
        AND player_name = 'Geofrey Gagganga';

    IF known_row_count <> 1 OR malformed_row_count + corrected_row_count <> 1 THEN
        RAISE EXCEPTION
            'Migration 012 expected exactly one known Gagganga goal row in malformed or corrected state; found total=%, malformed=%, corrected=%',
            known_row_count,
            malformed_row_count,
            corrected_row_count;
    END IF;

    UPDATE staging.events
    SET
        event_minute_text = '34',
        minute_base = 34,
        minute_added = 0,
        minute_total = 34,
        is_added_time = FALSE,
        minute_period = '31-45',
        staged_at = NOW()
    WHERE season = '2025_26'
        AND match_id = 31655
        AND match_url = 'https://upl.co.ug/event/nec-fc-vs-sc-villa-3/'
        AND event_type = 'goal'
        AND team_name = 'SC Villa'
        AND player_name = 'Geofrey Gagganga'
        AND event_minute_text = '334'
        AND minute_base = 334
        AND minute_added = 0
        AND minute_total = 334
        AND is_added_time IS FALSE
        AND minute_period = '90+';
END;
$$;

INSERT INTO analytics.team_season_point_adjustments (
    season,
    team_name,
    points_adjustment,
    note,
    updated_at
)
VALUES (
    '2025_26',
    'Buhimba United Saints FC',
    -3,
    'Official 2025/26 table adjustment: 15 sporting points become 12 official points after a three-point deduction.',
    NOW()
)
ON CONFLICT (season, team_name) DO UPDATE
SET
    points_adjustment = EXCLUDED.points_adjustment,
    note = EXCLUDED.note,
    updated_at = NOW();

CREATE OR REPLACE FUNCTION analytics.refresh_team_season_summary(_target_seasons TEXT[] DEFAULT NULL)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM analytics.team_season_summary
    WHERE _target_seasons IS NULL OR season = ANY(_target_seasons);

    INSERT INTO analytics.team_season_summary (
        season,
        team_name,
        matches_played,
        played_matches,
        administrative_matches,
        expected_matches,
        missing_matches,
        goals_for,
        goals_against,
        wins,
        draws,
        losses,
        sporting_points,
        administrative_points,
        points_adjustment,
        official_points,
        points_note,
        refreshed_at
    )
    WITH app_safe_matches AS (
        SELECT *
        FROM staging.matches
        WHERE is_source_anomaly IS NOT TRUE
            AND (_target_seasons IS NULL OR season = ANY(_target_seasons))
    ),
    season_team_counts AS (
        SELECT
            season,
            COUNT(DISTINCT team_name)::integer AS team_count,
            GREATEST((COUNT(DISTINCT team_name)::integer - 1) * 2, 0) AS expected_matches
        FROM (
            SELECT season, home_team AS team_name FROM app_safe_matches WHERE home_team IS NOT NULL
            UNION
            SELECT season, away_team AS team_name FROM app_safe_matches WHERE away_team IS NOT NULL
        ) AS teams
        GROUP BY season
    ),
    team_matches AS (
        SELECT
            season,
            home_team AS team_name,
            match_id,
            COALESCE(played_on_pitch, TRUE) AS played_on_pitch,
            COALESCE(is_administrative_result, FALSE) AS is_administrative_result,
            COALESCE(home_awarded_points, CASE WHEN result = 'home_win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) AS awarded_points,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS losses,
            COALESCE(home_score, 0)::integer AS goals_for,
            COALESCE(away_score, 0)::integer AS goals_against
        FROM app_safe_matches
        WHERE home_team IS NOT NULL
        UNION ALL
        SELECT
            season,
            away_team AS team_name,
            match_id,
            COALESCE(played_on_pitch, TRUE) AS played_on_pitch,
            COALESCE(is_administrative_result, FALSE) AS is_administrative_result,
            COALESCE(away_awarded_points, CASE WHEN result = 'away_win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) AS awarded_points,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS losses,
            COALESCE(away_score, 0)::integer AS goals_for,
            COALESCE(home_score, 0)::integer AS goals_against
        FROM app_safe_matches
        WHERE away_team IS NOT NULL
    ),
    team_summary AS (
        SELECT
            team_matches.season,
            team_matches.team_name,
            COUNT(*)::integer AS matches_played,
            COUNT(*) FILTER (WHERE played_on_pitch)::integer AS played_matches,
            COUNT(*) FILTER (WHERE is_administrative_result)::integer AS administrative_matches,
            COALESCE(season_team_counts.expected_matches, COUNT(*)::integer) AS expected_matches,
            GREATEST(COALESCE(season_team_counts.expected_matches, COUNT(*)::integer) - COUNT(*)::integer, 0) AS missing_matches,
            SUM(goals_for)::integer AS goals_for,
            SUM(goals_against)::integer AS goals_against,
            SUM(wins)::integer AS wins,
            SUM(draws)::integer AS draws,
            SUM(losses)::integer AS losses,
            SUM(awarded_points)::integer AS sporting_points,
            COALESCE(SUM(awarded_points) FILTER (WHERE is_administrative_result), 0)::integer AS administrative_points
        FROM team_matches
        LEFT JOIN season_team_counts
            ON season_team_counts.season = team_matches.season
        GROUP BY team_matches.season, team_matches.team_name, season_team_counts.expected_matches
    )
    SELECT
        team_summary.season,
        team_summary.team_name,
        team_summary.matches_played,
        team_summary.played_matches,
        team_summary.administrative_matches,
        team_summary.expected_matches,
        team_summary.missing_matches,
        team_summary.goals_for,
        team_summary.goals_against,
        team_summary.wins,
        team_summary.draws,
        team_summary.losses,
        team_summary.sporting_points,
        team_summary.administrative_points,
        COALESCE(adjustments.points_adjustment, 0) AS points_adjustment,
        team_summary.sporting_points + COALESCE(adjustments.points_adjustment, 0) AS official_points,
        NULLIF(CONCAT_WS(
            ' ',
            CASE
                WHEN team_summary.administrative_matches > 0
                THEN team_summary.administrative_matches || ' administrative result(s) included.'
            END,
            CASE
                WHEN team_summary.missing_matches > 0
                THEN team_summary.missing_matches || ' expected fixture(s) missing from app-safe data.'
            END,
            adjustments.note
        ), '') AS points_note,
        NOW() AS refreshed_at
    FROM team_summary
    LEFT JOIN analytics.team_season_point_adjustments AS adjustments
        ON adjustments.season = team_summary.season
        AND adjustments.team_name = team_summary.team_name;
END;
$$;

SELECT analytics.refresh_team_season_summary(NULL);
