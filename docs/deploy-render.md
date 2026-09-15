# Deploy alongside the existing Streamlit app

This deployment runs from `deploy/prophetic-render`, independently of `main` and the existing Streamlit service. Do not merge the website PRs into `main` as part of this launch: those changes remove the Streamlit entry point. No DNS changes or changes to the Streamlit deployment are needed.

## Create the new service

1. Sign in to [Render](https://dashboard.render.com/), select **New → Blueprint**, and connect `noah-art3mis/phantom-strategies`.
2. Choose branch **deploy/prophetic-render** and Blueprint path **render.yaml**.
3. Confirm the proposed resource is a new **prophetic-strategies-web** Docker web service on the **Free** plan. If that name is already in use in your Render workspace, choose a distinct name in the Blueprint before applying it.
4. Enter `OPENAI_API_KEY` in Render's prompted secret field. Use a key with access to the four existing fine-tuned models. Never commit it to Git or paste it into chat.
5. Create the Blueprint. Render builds the frontend and Python server in the Dockerfile and provides the service's public `onrender.com` URL with HTTPS.
6. Open the new URL and submit a question. `/api/health` should return `{"status":"ok"}`; the actual question confirms provider access as well.

The repository only includes configuration. Creating the Blueprint is the step that publishes the new service. The old Streamlit URL continues using its existing deployment.

## Updates

Auto-deploys are disabled. To release a later version, push the intended changes to `deploy/prophetic-render`, then use the new service's **Manual Deploy → Deploy latest commit** action. Changes to `main` do not deploy this service. Changes to this branch do not change the Streamlit app's configured branch.

## Free-tier behavior

Render's free web services sleep after 15 minutes without incoming traffic. A later request wakes the service, which can take about a minute. The workspace shares 750 free instance hours per month, and bandwidth/build allowances also apply. OpenAI requests are billed separately. All required corpus files are baked into the image; this app needs no persistent disk or external database.

See [Render free services](https://render.com/docs/free) and [Blueprint setup](https://render.com/docs/infrastructure-as-code).

## Local container check

```bash
docker build -t prophetic-strategies:local .
docker run --rm -p 8018:10000 prophetic-strategies:local
```

Open <http://localhost:8018>. Without credentials the UI and health endpoint work, and consultation returns an unavailable response. To test generation, export `OPENAI_API_KEY` in your shell and add `-e OPENAI_API_KEY` to `docker run` so Docker forwards it without placing its value in command history.
