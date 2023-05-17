# Personalized-Arxiv-digest
This repo aims to provide a better daily digest for newly published arxiv papers based on your own research interests and descriptions.

## Usage

### Running as a github action.

The recommended  way to get started using this repository is to:

1. Fork the repository
2. Modify `config.yaml` and merge the changes into your main branch. If you want a different schedule than Sunday through Thursday at 6:25AM, then also modify the file `.github/workflows/daily_pipeline.yaml`
3. Create or fetch api keys for openai and sendgrid
4. Set the following secrets. The two email keys only need to be included if you do not have them set in `config.yaml`:
  a. `OPENAI_API_KEY`
  b. `SENDGRID_API_KEY`
  c. `FROM_EMAIL`
  d. `TO_EMAIL`
5. Manually trigger the action or wait until the scheduled action takes place.

### Running from the command line

Install the requirements in `src/requirements.txt`

Make sure to set the configuration file `config.yaml` and the environment variables `OPENAI_API_KEY` and `SENDGRID_API_KEY`, and then run `python action.py`.

You may want to use something like `cron`.

### Running with a user interface

Install the requirements in `src/requirements.txt` as well as `gradio`. Set the evironment variables `OPENAI_API_KEY`, `FROM_EMAIL` and `SENDGRID_API_KEY`

Run `python src/app.py` and go to the local URL. From there you will be able to preview the papers from today, as well as the generated digests. 
