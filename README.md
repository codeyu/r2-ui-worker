# R2 UI Worker Deployer

This is a tool for deploying multiple R2 UI workers. You can use the code in the `./dist` folder directly, or build the code yourself.

### Requirements

- Node.js (v16+)
- Python (v3.x)
- pip (for Python package management)

### Installation

1. Clone this repository
   ```shell
   git clone https://github.com/codeyu/r2-ui-worker.git
   ```

2. Install Node.js dependencies
   ```shell
   npm install
   ```

3. Install Python dependencies
   ```shell
   pip install python-dotenv cloudflare
   ```

### Configuration

1. Copy the environment template file and edit it
   ```shell
   cp .env.example .env
   ```
   Edit `.env` and set your environment variables:
   - `CLOUDFLARE_TOKEN`: Your Cloudflare API token
   - `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
   - `AUTH_KEY_SECRET`: Your R2 UI authentication key

2. Configure your workers in `workers.json`:
   ```json
   {
     "workers": [
       {
         "worker_name": "worker1",
         "bucket_name": "bucket1"
       },
       {
         "worker_name": "worker2",
         "bucket_name": "bucket2"
       }
     ]
   }
   ```

### Deployment

#### Local Deployment

1. Login to Cloudflare (first time only)
   ```shell
   npx wrangler login
   ```

2. Run the deployment script
   ```shell
   python deploy.py
   ```

The script will:
- Check if each R2 bucket exists
- Create buckets if they don't exist
- Deploy workers with the specified configurations
- Set up authentication keys for each worker

#### GitHub Actions Deployment

1. Add the following secrets to your GitHub repository:
   - `CLOUDFLARE_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `AUTH_KEY_SECRET`

2. Push your code to the main branch, and GitHub Actions will automatically deploy your workers.

### How it Works

The deployment script will:
1. Read worker configurations from `workers.json`
2. Use Cloudflare's Python SDK to manage R2 buckets
3. For each worker:
   - Check if the R2 bucket exists, create if needed
   - Generate a custom `wrangler.toml` from the template
   - Deploy the worker to Cloudflare
   - Set up the AUTH_KEY_SECRET

### Notes

- Make sure to add `.env` to your `.gitignore`
- Each worker will be deployed with its own configuration
- The script uses Cloudflare's Python SDK for R2 bucket management
- Worker deployment still uses Wrangler CLI
- The deployment script will handle errors and provide feedback
- All environment variables are required for both local and GitHub Actions deployment

### Troubleshooting

If you encounter any issues:
1. Check that all environment variables are set correctly
2. Ensure your Cloudflare API token has the necessary permissions (R2:Edit and Workers:Edit)
3. Verify that your `workers.json` configuration is correct
4. Check the script output for specific error messages
