# papertrail_logs
Query Paper Trail Archives

This is a really dumb way to query papertrail archives.

## Instructions
- copy `.env-sample` to `.env`
- add your papertrail API key to the entry
- load ^env to your environment (example PyCharm env config)
- edit Line 132 in `main.py` to the starting date and query to search for
- run

## Notes
- This downloads each file (1 per hour of timestamp, i.e. 24 files for a 1-day duration), extracts, searches the text line-by-line and then deletes it
- Takes about 30s to download, a bit to extract, and around 30s to read -> so ~1 minute per file to execute
- This means to complete a day's query, it will take about 24 minutes, to complete a month, almost half a day ¯\_(ツ)_/¯
- Each hour's log is deleted after reading through as they are huge files
- If not using debugger, write out the dataframe somewhere before running