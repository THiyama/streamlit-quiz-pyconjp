use role accountadmin;
grant usage on warehouse compute_wh to role public;

use role sysadmin;
use warehouse compute_wh;
create database streamlit_quiz;
use schema streamlit_quiz.public;


use role sysadmin;
create or replace TABLE streamlit_quiz.PUBLIC.SUBMIT2 (
	TEAM_ID VARCHAR(16777216),
	PROBLEM_ID VARCHAR(16777216),
	TIMESTAMP TIMESTAMP_NTZ(9),
	IS_CLEAR BOOLEAN,
	KEY VARCHAR(16777216),
	MAX_ATTEMPTS NUMBER(38,0)
);


use role accountadmin;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
select snowflake.cortex.complete('snowflake-arctic', 'こんにちは。あなたは誰ですか？');