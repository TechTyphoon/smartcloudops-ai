# Security Audit Report - Smart CloudOps AI

**Generated**: 2025-08-10T12:14:33.621264  
**Overall Security Score**: 0/100 (F)

## 🚨 Critical Issues (0)

## ⚠️ High Priority Issues (3)

- **requirements.txt:N/A** - Vulnerable package version: flask 2.3.3
  - Minimum safe version: <2.0.0

- **requirements.txt:N/A** - Vulnerable package version: requests 2.31.0
  - Minimum safe version: <2.25.0

- **terraform/main.tf:N/A** - Open security group rule
  - Security group allows access from 0.0.0.0/0

## 🔶 Medium Priority Issues (1416)

- **venv/lib/python3.13/site-packages/fsspec/spec.py:1640** - Potential hardcoded_secrets
  - Pattern matched: password='password'

- **venv/lib/python3.13/site-packages/pydantic/types.py:1695** - Potential hardcoded_secrets
  - Pattern matched: password='password1'

- **venv/lib/python3.13/site-packages/httpx/_urls.py:336** - Potential hardcoded_secrets
  - Pattern matched: password="a secret"

- **venv/lib/python3.13/site-packages/bandit/plugins/general_hardcoded_password.py:164** - Potential hardcoded_secrets
  - Pattern matched: password="blerg"

- **venv/lib/python3.13/site-packages/bandit/plugins/general_hardcoded_password.py:222** - Potential hardcoded_secrets
  - Pattern matched: password="Admin"

- **venv/lib/python3.13/site-packages/pip/_internal/utils/misc.py:470** - Potential hardcoded_secrets
  - Pattern matched: password = ":****"

- **venv/lib/python3.13/site-packages/checkov/common/util/secrets.py:23** - Potential hardcoded_secrets
  - Pattern matched: PASSWORD = 'password'

- **venv/lib/python3.13/site-packages/detect_secrets/plugins/keyword.py:156** - Potential hardcoded_secrets
  - Pattern matched: password = "bar"

- **venv/lib/python3.13/site-packages/detect_secrets/plugins/keyword.py:192** - Potential hardcoded_secrets
  - Pattern matched: password = "bar"

- **venv/lib/python3.13/site-packages/cyclonedx/model/crypto.py:703** - Potential hardcoded_secrets
  - Pattern matched: PASSWORD = 'password'

- **.formatvenv/lib/python3.13/site-packages/pydantic/types.py:1819** - Potential hardcoded_secrets
  - Pattern matched: password='password1'

- **.formatvenv/lib/python3.13/site-packages/pydantic/types.py:1846** - Potential hardcoded_secrets
  - Pattern matched: password='IAmSensitive'

- **.formatvenv/lib/python3.13/site-packages/httpx/_urls.py:336** - Potential hardcoded_secrets
  - Pattern matched: password="a secret"

- **.formatvenv/lib/python3.13/site-packages/pip/_internal/utils/misc.py:478** - Potential hardcoded_secrets
  - Pattern matched: password = ":****"

- **.venv/lib/python3.12/site-packages/pip/_internal/utils/misc.py:470** - Potential hardcoded_secrets
  - Pattern matched: password = ":****"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9177** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9228** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9291** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9299** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9368** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9376** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9431** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:9482** - Potential hardcoded_secrets
  - Pattern matched: secret="my-secret"

- **venv/lib/python3.13/site-packages/huggingface_hub/_webhooks_server.py:87** - Potential hardcoded_secrets
  - Pattern matched: secret="my_secret_key"

- **venv/lib/python3.13/site-packages/huggingface_hub/_webhooks_server.py:328** - Potential hardcoded_secrets
  - Pattern matched: secret='my_secret'

- **venv/lib/python3.13/site-packages/openai/resources/webhooks.py:66** - Potential hardcoded_secrets
  - Pattern matched: secret='123'

- **venv/lib/python3.13/site-packages/openai/resources/webhooks.py:163** - Potential hardcoded_secrets
  - Pattern matched: secret='123'

- **venv/lib/python3.13/site-packages/litellm/secret_managers/aws_secret_manager_v2.py:101** - Potential hardcoded_secrets
  - Pattern matched: secret='%s'

- **venv/lib/python3.13/site-packages/litellm/secret_managers/aws_secret_manager_v2.py:153** - Potential hardcoded_secrets
  - Pattern matched: secret='%s'

- **venv/lib/python3.13/site-packages/litellm/secret_managers/aws_secret_manager_v2.py:160** - Potential hardcoded_secrets
  - Pattern matched: secret='%s'

- **venv/lib/python3.13/site-packages/cyclonedx/model/crypto.py:709** - Potential hardcoded_secrets
  - Pattern matched: SECRET = 'shared-secret'

- **venv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:30** - Potential hardcoded_secrets
  - Pattern matched: SECRET = "%(secret)s"

- **.formatvenv/lib/python3.13/site-packages/openai/resources/webhooks.py:66** - Potential hardcoded_secrets
  - Pattern matched: secret='123'

- **.formatvenv/lib/python3.13/site-packages/openai/resources/webhooks.py:163** - Potential hardcoded_secrets
  - Pattern matched: secret='123'

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:30** - Potential hardcoded_secrets
  - Pattern matched: SECRET = "%(secret)s"

- **tests/test_chatops.py:93** - Potential hardcoded_secrets
  - Pattern matched: api_key='test-key'

- **tests/test_ai_handler.py:152** - Potential hardcoded_secrets
  - Pattern matched: api_key="test-key"

- **scripts/env_manager.py:39** - Potential hardcoded_secrets
  - Pattern matched: API_KEY='your_gemini_key_here'

- **scripts/env_manager.py:40** - Potential hardcoded_secrets
  - Pattern matched: API_KEY='your_openai_key_here'

- **venv/lib/python3.13/site-packages/litellm/main.py:738** - Potential hardcoded_secrets
  - Pattern matched: api_key="mock-key"

- **venv/lib/python3.13/site-packages/litellm/main.py:831** - Potential hardcoded_secrets
  - Pattern matched: api_key="my-secret-key"

- **venv/lib/python3.13/site-packages/litellm/utils.py:7504** - Potential hardcoded_secrets
  - Pattern matched: api_key="my-fake-api-key"

- **venv/lib/python3.13/site-packages/safety/scan/util.py:61** - Potential hardcoded_secrets
  - Pattern matched: api_key = "api_key"

- **venv/lib/python3.13/site-packages/google/generativeai/generative_models.py:38** - Potential hardcoded_secrets
  - Pattern matched: api_key='YOUR_API_KEY'

- **venv/lib/python3.13/site-packages/safety_schemas/models/base.py:89** - Potential hardcoded_secrets
  - Pattern matched: API_KEY = "api_key"

- **venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py:143** - Potential hardcoded_secrets
  - Pattern matched: api_key = "api_key"

- **venv/lib/python3.13/site-packages/checkov/common/output/csv.py:44** - Potential hardcoded_secrets
  - Pattern matched: API_KEY = "SCA, image and runtime findings are only available with a Prisma Cloud subscription."

- **venv/lib/python3.13/site-packages/litellm/types/mcp.py:31** - Potential hardcoded_secrets
  - Pattern matched: api_key = "api_key"

- **venv/lib/python3.13/site-packages/litellm/proxy/_types.py:2805** - Potential hardcoded_secrets
  - Pattern matched: api_key = "x-litellm-api-key"

- **venv/lib/python3.13/site-packages/litellm/proxy/proxy_server.py:6271** - Potential hardcoded_secrets
  - Pattern matched: api_key = "null"

- **venv/lib/python3.13/site-packages/litellm/proxy/proxy_server.py:6383** - Potential hardcoded_secrets
  - Pattern matched: api_key = "null"

- **venv/lib/python3.13/site-packages/litellm/proxy/proxy_server.py:6477** - Potential hardcoded_secrets
  - Pattern matched: api_key = "null"

- **venv/lib/python3.13/site-packages/litellm/proxy/proxy_cli.py:80** - Potential hardcoded_secrets
  - Pattern matched: api_key="My API Key"

- **venv/lib/python3.13/site-packages/litellm/llms/watsonx/common_utils.py:273** - Potential hardcoded_secrets
  - Pattern matched: api_key='."

- **venv/lib/python3.13/site-packages/litellm/llms/gemini/google_genai/transformation.py:38** - Potential hardcoded_secrets
  - Pattern matched: API_KEY = "x-goog-api-key"

- **venv/lib/python3.13/site-packages/litellm/integrations/prometheus_helpers/prometheus_api.py:113** - Potential hardcoded_secrets
  - Pattern matched: api_key="{api_key}"

- **venv/lib/python3.13/site-packages/litellm/integrations/SlackAlerting/slack_alerting.py:1062** - Potential hardcoded_secrets
  - Pattern matched: api_key="your_api_key"

- **venv/lib/python3.13/site-packages/litellm/integrations/email_templates/templates.py:24** - Potential hardcoded_secrets
  - Pattern matched: api_key="{key_token}"

- **venv/lib/python3.13/site-packages/litellm/proxy/vertex_ai_endpoints/langfuse_endpoints.py:69** - Potential hardcoded_secrets
  - Pattern matched: api_key="Bearer {}"

- **venv/lib/python3.13/site-packages/litellm/proxy/example_config_yaml/custom_auth_basic.py:9** - Potential hardcoded_secrets
  - Pattern matched: api_key="best-api-key-ever"

- **venv/lib/python3.13/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py:196** - Potential hardcoded_secrets
  - Pattern matched: api_key = "litellm_proxy_master_key"

- **venv/lib/python3.13/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py:225** - Potential hardcoded_secrets
  - Pattern matched: api_key = "litellm_proxy_master_key"

- **venv/lib/python3.13/site-packages/litellm/proxy/spend_tracking/spend_management_endpoints.py:942** - Potential hardcoded_secrets
  - Pattern matched: api_key='sk-1234"

- **venv/lib/python3.13/site-packages/litellm/types/proxy/management_endpoints/common_daily_activity.py:11** - Potential hardcoded_secrets
  - Pattern matched: API_KEY = "api_key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:708** - Potential hardcoded_secrets
  - Pattern matched: api_key="<together_api_key>"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:722** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2434** - Potential hardcoded_secrets
  - Pattern matched: api_key="fal-ai-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2448** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2462** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2546** - Potential hardcoded_secrets
  - Pattern matched: api_key="fal-ai-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2561** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2701** - Potential hardcoded_secrets
  - Pattern matched: api_key="your-replicate-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2715** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_client.py:2728** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:745** - Potential hardcoded_secrets
  - Pattern matched: api_key="<together_api_key>"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:759** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2491** - Potential hardcoded_secrets
  - Pattern matched: api_key="fal-ai-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2505** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2519** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2603** - Potential hardcoded_secrets
  - Pattern matched: api_key="fal-ai-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2618** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2759** - Potential hardcoded_secrets
  - Pattern matched: api_key="your-replicate-api-key"

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2773** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **venv/lib/python3.13/site-packages/huggingface_hub/inference/_generated/_async_client.py:2786** - Potential hardcoded_secrets
  - Pattern matched: api_key="hf_..."

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/generative_models.py:38** - Potential hardcoded_secrets
  - Pattern matched: api_key='YOUR_API_KEY'

- **venv/lib/python3.13/site-packages/pycodestyle.py:2611** - Potential hardcoded_secrets
  - Pattern matched: token=','

- **venv/lib/python3.13/site-packages/git/remote.py:257** - Potential hardcoded_secrets
  - Pattern matched: token = "..."

- **venv/lib/python3.13/site-packages/git/remote.py:259** - Potential hardcoded_secrets
  - Pattern matched: token = ".."

- **venv/lib/python3.13/site-packages/git/remote.py:444** - Potential hardcoded_secrets
  - Pattern matched: token = "..."

- **venv/lib/python3.13/site-packages/git/remote.py:767** - Potential hardcoded_secrets
  - Pattern matched: token = " * [would prune] "

- **venv/lib/python3.13/site-packages/git/util.py:591** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "done."

- **venv/lib/python3.13/site-packages/grpc/_server.py:63** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "receive_close_on_server"

- **venv/lib/python3.13/site-packages/grpc/_server.py:64** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_initial_metadata"

- **venv/lib/python3.13/site-packages/grpc/_server.py:65** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "receive_message"

- **venv/lib/python3.13/site-packages/grpc/_server.py:66** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_message"

- **venv/lib/python3.13/site-packages/grpc/_server.py:70** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_status_from_server"

- **venv/lib/python3.13/site-packages/huggingface_hub/constants.py:286** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "X-Xet-Access-Token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4671** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4679** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4687** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4905** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4917** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/hf_api.py:4928** - Potential hardcoded_secrets
  - Pattern matched: token="my_token"

- **venv/lib/python3.13/site-packages/botocore/credentials.py:1911** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'AWS_CONTAINER_AUTHORIZATION_TOKEN'

- **venv/lib/python3.13/site-packages/dateutil/parser/_parser.py:122** - Potential hardcoded_secrets
  - Pattern matched: token = ' '

- **venv/lib/python3.13/site-packages/safety/scan/util.py:60** - Potential hardcoded_secrets
  - Pattern matched: token = "token"

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/ttProgram.py:201** - Potential hardcoded_secrets
  - Pattern matched: token = "(%s)|(%s)|(%s)"

- **venv/lib/python3.13/site-packages/tqdm/contrib/telegram.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/tqdm/contrib/telegram.py:102** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/tqdm/contrib/discord.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/tqdm/contrib/discord.py:105** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/tqdm/contrib/slack.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/tqdm/contrib/slack.py:68** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **venv/lib/python3.13/site-packages/authlib/oauth1/rfc5849/signature.py:39** - Potential hardcoded_secrets
  - Pattern matched: token="kkk9d7dh3k39sjv7"

- **venv/lib/python3.13/site-packages/authlib/oauth1/rfc5849/authorization_server.py:215** - Potential hardcoded_secrets
  - Pattern matched: token="hh5s93j4hdidpola"

- **venv/lib/python3.13/site-packages/google/auth/environment_vars.py:82** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "AWS_SESSION_TOKEN"

- **venv/lib/python3.13/site-packages/google/auth/metrics.py:30** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "auth-request-type/at"

- **venv/lib/python3.13/site-packages/google/auth/metrics.py:31** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "auth-request-type/it"

- **venv/lib/python3.13/site-packages/google/protobuf/text_format.py:897** - Potential hardcoded_secrets
  - Pattern matched: token = '>'

- **venv/lib/python3.13/site-packages/google/protobuf/text_format.py:900** - Potential hardcoded_secrets
  - Pattern matched: token = '}'

- **venv/lib/python3.13/site-packages/google/protobuf/text_format.py:1058** - Potential hardcoded_secrets
  - Pattern matched: token = '>'

- **venv/lib/python3.13/site-packages/google/protobuf/text_format.py:1061** - Potential hardcoded_secrets
  - Pattern matched: token = '}'

- **venv/lib/python3.13/site-packages/google/api_core/page_iterator.py:320** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "pageToken"

- **venv/lib/python3.13/site-packages/google/api_core/page_iterator.py:322** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "nextPageToken"

- **venv/lib/python3.13/site-packages/google/auth/aio/credentials.py:92** - Potential hardcoded_secrets
  - Pattern matched: token="token123"

- **venv/lib/python3.13/site-packages/safety_schemas/models/base.py:88** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "token"

- **venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py:142** - Potential hardcoded_secrets
  - Pattern matched: token = "token"

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:25** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'iamRoleStatements'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:26** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'resources'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:27** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'provider'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:28** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'functions'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:29** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'environment'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:30** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'stackTags'

- **venv/lib/python3.13/site-packages/checkov/serverless/parsers/parser.py:31** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'tags'

- **venv/lib/python3.13/site-packages/nltk/tokenize/treebank.py:249** - Potential hardcoded_secrets
  - Pattern matched: token = 'Good muffins cost $3.88 in New (York). Please (buy) me two of them. (Thanks).'

- **venv/lib/python3.13/site-packages/litellm/types/mcp.py:32** - Potential hardcoded_secrets
  - Pattern matched: token = "bearer_token"

- **venv/lib/python3.13/site-packages/litellm/proxy/utils.py:2234** - Potential hardcoded_secrets
  - Pattern matched: token = '{token}'

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:124** - Potential hardcoded_secrets
  - Pattern matched: token="<s>"

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:125** - Potential hardcoded_secrets
  - Pattern matched: token="</s>"

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:148** - Potential hardcoded_secrets
  - Pattern matched: token="<s>"

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:149** - Potential hardcoded_secrets
  - Pattern matched: token="</s>"

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:431** - Potential hardcoded_secrets
  - Pattern matched: token="<eos>"

- **venv/lib/python3.13/site-packages/litellm/litellm_core_utils/prompt_templates/factory.py:432** - Potential hardcoded_secrets
  - Pattern matched: token="<bos>"

- **venv/lib/python3.13/site-packages/litellm/llms/bedrock/chat/invoke_transformations/amazon_deepseek_transformation.py:64** - Potential hardcoded_secrets
  - Pattern matched: token = "<think>"

- **venv/lib/python3.13/site-packages/litellm/proxy/auth/auth_checks.py:1002** - Potential hardcoded_secrets
  - Pattern matched: token="ui-token"

- **venv/lib/python3.13/site-packages/litellm/proxy/auth/auth_exception_handler.py:69** - Potential hardcoded_secrets
  - Pattern matched: token="failed-to-connect-to-db"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_headers.py:97** - Potential hardcoded_secrets
  - Pattern matched: token="hf_***"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_validators.py:76** - Potential hardcoded_secrets
  - Pattern matched: token="a token"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_validators.py:79** - Potential hardcoded_secrets
  - Pattern matched: token="a use_auth_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_validators.py:82** - Potential hardcoded_secrets
  - Pattern matched: token="a token"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_validators.py:82** - Potential hardcoded_secrets
  - Pattern matched: token="a use_auth_token"

- **venv/lib/python3.13/site-packages/huggingface_hub/utils/_validators.py:96** - Potential hardcoded_secrets
  - Pattern matched: token = "use_auth_token"

- **venv/lib/python3.13/site-packages/cyclonedx/model/crypto.py:712** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = 'token'

- **venv/lib/python3.13/site-packages/argcomplete/packages/_shlex.py:130** - Potential hardcoded_secrets
  - Pattern matched: token=" + repr(raw))
            else:
                print("

- **venv/lib/python3.13/site-packages/argcomplete/packages/_shlex.py:277** - Potential hardcoded_secrets
  - Pattern matched: token=" + repr(result))
            else:
                print("

- **.formatvenv/lib/python3.13/site-packages/pycodestyle.py:2611** - Potential hardcoded_secrets
  - Pattern matched: token=','

- **.formatvenv/lib/python3.13/site-packages/grpc/_server.py:63** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "receive_close_on_server"

- **.formatvenv/lib/python3.13/site-packages/grpc/_server.py:64** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_initial_metadata"

- **.formatvenv/lib/python3.13/site-packages/grpc/_server.py:65** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "receive_message"

- **.formatvenv/lib/python3.13/site-packages/grpc/_server.py:66** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_message"

- **.formatvenv/lib/python3.13/site-packages/grpc/_server.py:70** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "send_status_from_server"

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/telegram.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/telegram.py:102** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/discord.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/discord.py:105** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/slack.py:6** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/tqdm/contrib/slack.py:68** - Potential hardcoded_secrets
  - Pattern matched: token='{token}'

- **.formatvenv/lib/python3.13/site-packages/google/auth/environment_vars.py:82** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "AWS_SESSION_TOKEN"

- **.formatvenv/lib/python3.13/site-packages/google/auth/metrics.py:30** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "auth-request-type/at"

- **.formatvenv/lib/python3.13/site-packages/google/auth/metrics.py:31** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "auth-request-type/it"

- **.formatvenv/lib/python3.13/site-packages/google/protobuf/text_format.py:897** - Potential hardcoded_secrets
  - Pattern matched: token = '>'

- **.formatvenv/lib/python3.13/site-packages/google/protobuf/text_format.py:900** - Potential hardcoded_secrets
  - Pattern matched: token = '}'

- **.formatvenv/lib/python3.13/site-packages/google/protobuf/text_format.py:1058** - Potential hardcoded_secrets
  - Pattern matched: token = '>'

- **.formatvenv/lib/python3.13/site-packages/google/protobuf/text_format.py:1061** - Potential hardcoded_secrets
  - Pattern matched: token = '}'

- **.formatvenv/lib/python3.13/site-packages/google/api_core/page_iterator.py:320** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "pageToken"

- **.formatvenv/lib/python3.13/site-packages/google/api_core/page_iterator.py:322** - Potential hardcoded_secrets
  - Pattern matched: TOKEN = "nextPageToken"

- **.formatvenv/lib/python3.13/site-packages/google/auth/aio/credentials.py:92** - Potential hardcoded_secrets
  - Pattern matched: token="token123"

- **venv/lib/python3.13/site-packages/coverage/sqldata.py:687** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, context.context, arc.fromno, arc.tono " +
                "from arc " +
                "inner join file on file.id = arc.file_id " +

- **venv/lib/python3.13/site-packages/coverage/sqldata.py:699** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, context.context, line_bits.numbits " +
                "from line_bits " +
                "inner join file on file.id = line_bits.file_id " +

- **venv/lib/python3.13/site-packages/coverage/sqldata.py:713** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, tracer " +
                "from tracer " +

- **venv/lib/python3.13/site-packages/coverage/sqldata.py:730** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, tracer from tracer " +

- **venv/lib/python3.13/site-packages/coverage/sqldata.py:938** - Potential sql_injection
  - Pattern matched: execute("select id from context where " +

- **.formatvenv/lib/python3.13/site-packages/coverage/sqldata.py:687** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, context.context, arc.fromno, arc.tono " +
                "from arc " +
                "inner join file on file.id = arc.file_id " +

- **.formatvenv/lib/python3.13/site-packages/coverage/sqldata.py:699** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, context.context, line_bits.numbits " +
                "from line_bits " +
                "inner join file on file.id = line_bits.file_id " +

- **.formatvenv/lib/python3.13/site-packages/coverage/sqldata.py:713** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, tracer " +
                "from tracer " +

- **.formatvenv/lib/python3.13/site-packages/coverage/sqldata.py:730** - Potential sql_injection
  - Pattern matched: execute(
                "select file.path, tracer from tracer " +

- **.formatvenv/lib/python3.13/site-packages/coverage/sqldata.py:938** - Potential sql_injection
  - Pattern matched: execute("select id from context where " +

- **tests/test_integration.py:271** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/_pytest/capture.py:1043** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/_pytest/capture.py:1071** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/pbr/testr_command.py:142** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/pbr/testr_command.py:143** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/pbr/testr_command.py:144** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:380** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:388** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:460** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:499** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:604** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/click/_termui_impl.py:613** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/PIL/ImageShow.py:120** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/bandit/plugins/injection_shell.py:464** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/build/build.py:68** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/build/build.py:97** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/build/build.py:112** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/build/build.py:116** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/python/tbb/__init__.py:56** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/numpy/f2py/diagnose.py:9** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/detect_secrets/audit/io.py:26** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/fsspec/tests/abstract/mv.py:36** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/fsspec/tests/abstract/mv.py:55** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_rcparams.py:299** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/psutil/tests/__init__.py:1429** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/psutil/tests/__init__.py:1431** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/_pytest/capture.py:1043** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/_pytest/capture.py:1071** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:380** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:388** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:460** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:499** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:604** - Potential command_injection
  - Pattern matched: os.system(

- **.formatvenv/lib/python3.13/site-packages/click/_termui_impl.py:613** - Potential command_injection
  - Pattern matched: os.system(

- **venv/lib/python3.13/site-packages/safety/scan/util.py:130** - Potential command_injection
  - Pattern matched: subprocess.run(
                    self.git +

- **tests/test_chatops.py:70** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:1444** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:3967** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:3972** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:4019** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:4031** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:4036** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/typing_extensions.py:4064** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/configargparse.py:253** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/configargparse.py:394** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/configargparse.py:399** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/configargparse.py:593** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/psutil/__init__.py:1922** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:347** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:485** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:802** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:827** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:830** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:834** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/rcsetup.py:1104** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rich/markup.py:190** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/asteval/asteval.py:275** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/asteval/asteval.py:328** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/asteval/asteval.py:330** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/skipping.py:87** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/skipping.py:116** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/pytester.py:292** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fsspec/gui.py:312** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/wheel.py:190** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/wheel.py:211** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/huggingface_hub/hub_mixin.py:718** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/huggingface_hub/hub_mixin.py:826** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/utils.py:5015** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/internals.py:231** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/decorators.py:136** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/decorators.py:204** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/collocations.py:398** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/collocations.py:402** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/isort/literal.py:54** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/ply/yacc.py:1564** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/ply/cpp.py:609** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/parallel.py:1749** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/parallel.py:1778** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/memory.py:178** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/memory.py:1179** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/packaging/_parser.py:337** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pyparsing/results.py:62** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/lark/load_grammar.py:559** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/flask/cli.py:150** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/flask/cli.py:152** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/flask/cli.py:1031** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pymeeus/Angle.py:1212** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/prophet/diagnostics.py:394** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/coverage/parser.py:662** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/gunicorn/util.py:398** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/gunicorn/util.py:399** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/serializable/__init__.py:957** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/serializable/__init__.py:958** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/serializable/__init__.py:990** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/serializable/__init__.py:991** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/jinja2/nativetypes.py:40** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/jinja2/lexer.py:663** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/jinja2/nodes.py:581** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/GifImagePlugin.py:732** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/GifImagePlugin.py:754** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:236** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:278** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:284** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:335** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:342** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:350** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:350** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/ImageMath.py:368** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/PIL/Image.py:3642** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/cffi/recompiler.py:78** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:212** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:223** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:256** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:1635** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:1755** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/attr/_make.py:1829** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/graph.py:635** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/graph.py:2180** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/graph.py:2880** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:233** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:261** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:286** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:343** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:377** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/paths.py:497** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/tqdm/cli.py:38** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/bandit/plugins/logging_config_insecure_listen.py:13** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4828** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4844** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4848** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4851** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4902** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4913** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4930** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/frame.py:4954** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/errors/__init__.py:567** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/errors/__init__.py:585** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/ops.py:431** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:482** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:517** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:521** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:531** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:578** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/expr.py:586** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/eval.py:173** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/eval.py:297** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/core/computation/scope.py:199** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/generic/test_finalize.py:449** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:146** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:154** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:167** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:181** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:189** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:198** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:226** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:241** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:252** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:265** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:274** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:279** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:299** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:306** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:326** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:335** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:347** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:362** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:375** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:388** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:392** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:399** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:402** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:408** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:417** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:421** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:433** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:437** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:444** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:447** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:453** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:464** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:468** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:476** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:482** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:490** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:493** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:502** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:508** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:516** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:519** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:537** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:555** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:564** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:566** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:567** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:568** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:569** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:570** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:574** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:578** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:579** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:580** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:581** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:582** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:589** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:613** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:620** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:626** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:648** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:653** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:658** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:663** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:669** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:674** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:679** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:687** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:693** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:730** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:731** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:732** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:737** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:738** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:758** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:768** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:790** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:813** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:815** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:828** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:836** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:864** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:866** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:886** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:888** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:927** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:929** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:957** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:959** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:961** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:962** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1010** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1012** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1025** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1029** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1034** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1047** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1066** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1068** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1091** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1094** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1098** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1102** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1114** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1117** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1118** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1130** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1133** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1134** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1142** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1145** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1150** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1156** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1160** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1177** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1187** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1195** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1204** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1212** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1221** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1231** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1240** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1253** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1263** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1266** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1273** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1281** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1294** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1308** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1319** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1331** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1345** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1355** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1371** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1391** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1411** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1441** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1450** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1454** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1462** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1468** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1472** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1480** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1491** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1500** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1507** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1518** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1521** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1524** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1527** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1530** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1533** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1536** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1539** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1542** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1545** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1550** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1552** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1554** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1556** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1559** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1561** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1567** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1586** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1594** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1608** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1611** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1615** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1617** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1628** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1645** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1657** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1674** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1699** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1711** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1718** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1728** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1734** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1742** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1751** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1758** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1765** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1801** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1826** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1833** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1842** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1845** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1853** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1855** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1862** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1868** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1873** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1895** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1907** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1919** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:1983** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py:2000** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/computation/test_compat.py:31** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/test_old_base.py:238** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/copy_view/test_methods.py:2015** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/copy_view/test_methods.py:2019** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/copy_view/test_methods.py:2034** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:60** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:66** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:72** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:79** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:90** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:117** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:120** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:168** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:169** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:179** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:187** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:191** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:199** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:203** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:206** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:620** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:623** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:629** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:871** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:886** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:890** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1176** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1181** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1191** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1240** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1245** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1250** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1255** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1260** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1265** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1270** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1275** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1280** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1305** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1317** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1347** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1350** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1353** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1362** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1375** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/test_query_eval.py:1386** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/methods/test_sample.py:176** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/frame/methods/test_sample.py:177** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/io/xml/test_xml.py:1272** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/io/xml/test_to_xml.py:1105** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/base_class/test_formats.py:16** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/categorical/test_category.py:203** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/numeric/test_numeric.py:43** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/multi/test_formats.py:64** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/ranges/test_range.py:63** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/ranges/test_range.py:71** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/indexes/ranges/test_range.py:398** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_constructors.py:652** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_constructors.py:660** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_constructors.py:669** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_constructors.py:677** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_formats.py:110** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_formats.py:116** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_formats.py:126** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pandas/tests/scalar/timestamp/test_formats.py:163** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_decor/wrap/__init__.py:360** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdresolve.py:211** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdresolve.py:249** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdresolve.py:563** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdresolve.py:744** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:210** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:291** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:293** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:294** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:297** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:302** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/beartype/_check/code/__init__.py:2133** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/misc/symfont.py:241** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/misc/xmlReader.py:106** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/misc/xmlReader.py:122** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/cffLib/__init__.py:1100** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/cffLib/__init__.py:1267** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/cffLib/__init__.py:1718** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/cffLib/__init__.py:1883** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/cffLib/__init__.py:2026** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/feaLib/builder.py:499** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_p_o_s_t.py:263** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:130** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:134** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:135** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:136** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:145** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F__e_a_t.py:145** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:206** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:220** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:221** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:222** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:223** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:224** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:245** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:246** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_D_M_X_.py:247** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S_V_G_.py:186** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_t_r_a_k.py:118** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_t_r_a_k.py:120** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_t_r_a_k.py:292** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_t_r_a_k.py:300** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/M_E_T_A_.py:211** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/M_E_T_A_.py:243** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/M_E_T_A_.py:286** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/M_E_T_A_.py:328** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:276** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:795** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:795** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:796** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:797** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:799** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:1916** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:1917** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:1919** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:1920** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_l_y_f.py:1934** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_l.py:81** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_l.py:91** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otBase.py:951** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otBase.py:989** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otBase.py:1093** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otBase.py:1135** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/O_S_2f_2.py:42** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/O_S_2f_2.py:253** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/O_S_2f_2.py:255** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_v_h_e_a.py:130** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_s_b_i_x.py:109** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:316** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:415** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:416** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:417** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:607** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S__i_l_f.py:772** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S_I_N_G_.py:66** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/S_I_N_G_.py:99** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G__l_o_c.py:76** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:350** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:352** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:354** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:355** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:358** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:360** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:365** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:546** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:548** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:550** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:609** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:614** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:616** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:618** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:747** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:752** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:758** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:869** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1097** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1098** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1099** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1153** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1154** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1725** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otTables.py:1908** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_h_h_e_a.py:147** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_a_s_p.py:61** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_a_s_p.py:61** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/TupleVariation.py:121** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/TupleVariation.py:122** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/TupleVariation.py:123** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/TupleVariation.py:126** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/TupleVariation.py:127** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/C_P_A_L_.py:268** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/C_P_A_L_.py:269** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/C_P_A_L_.py:276** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_a_v_a_r.py:124** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_a_v_a_r.py:125** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G_P_K_G_.py:133** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/T_S_I__5.py:60** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_m_a_x_p.py:147** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/L_T_S_H_.py:58** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_n_a_m_e.py:621** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_n_a_m_e.py:622** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_n_a_m_e.py:623** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_n_a_m_e.py:624** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_n_a_m_e.py:627** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_h_d_m_x.py:123** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:114** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:115** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:116** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:155** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:156** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/D_S_I_G_.py:157** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_v_a_r.py:257** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_g_v_a_r.py:259** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixGlyph.py:141** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_f_v_a_r.py:175** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_f_v_a_r.py:251** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_f_v_a_r.py:252** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_f_v_a_r.py:254** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:174** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:178** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:186** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:227** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:331** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:333** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:334** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:377** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:379** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:380** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_D_T_.py:475** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:140** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:143** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:147** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:149** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:155** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/sbixStrike.py:159** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/C_O_L_R_.py:108** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/C_O_L_R_.py:165** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G_M_A_P_.py:56** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G_M_A_P_.py:148** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_h_m_t_x.py:149** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_h_m_t_x.py:150** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G__l_a_t.py:202** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G__l_a_t.py:203** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G__l_a_t.py:215** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/G__l_a_t.py:216** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_l_t_a_g.py:71** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:80** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:623** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1217** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1232** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1234** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1534** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1554** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1564** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1595** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1642** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1706** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1805** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/otConverters.py:1819** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:254** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:258** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:296** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:342** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:364** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:432** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:433** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:434** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/E_B_L_C_.py:569** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_v_t.py:40** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_v_t.py:41** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:238** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:244** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:246** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:247** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:419** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:429** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:772** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:783** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1055** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1066** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1122** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1133** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1290** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1291** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1292** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1293** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1294** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1305** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1456** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_c_m_a_p.py:1457** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/BitmapGlyphMetrics.py:50** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_O_R_G_.py:119** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/V_O_R_G_.py:165** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_h_e_a_d.py:129** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:98** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:104** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:236** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:237** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:240** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/_k_e_r_n.py:254** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/fontTools/ttLib/tables/F_F_T_M_.py:51** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:301** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:498** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:500** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:538** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:540** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:543** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/tools/csv2rdf.py:545** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/parserutils.py:76** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/parserutils.py:222** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evalutils.py:88** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evalutils.py:103** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evalutils.py:111** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evalutils.py:118** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evalutils.py:126** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:55** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:86** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:127** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:155** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:201** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:204** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:237** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/aggregates.py:262** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evaluate.py:132** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/rdflib/plugins/sparql/evaluate.py:484** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pip/_vendor/rich/markup.py:190** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pip/_vendor/packaging/_parser.py:332** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pip/_vendor/packaging/licenses/__init__.py:100** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pip/_vendor/pygments/formatters/__init__.py:91** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:697** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:708** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:745** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:760** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:829** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/ai/generativelanguage_v1alpha/types/content.py:368** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/google/ai/generativelanguage_v1alpha/types/content.py:408** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/google/ai/generativelanguage_v1beta/types/content.py:368** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/google/ai/generativelanguage_v1beta/types/content.py:408** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/readwrite/gml.py:109** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/readwrite/multiline_adjlist.py:294** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/readwrite/edgelist.py:272** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/algorithms/bipartite/edgelist.py:242** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/algorithms/operators/tests/test_all.py:27** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/algorithms/operators/tests/test_binary.py:22** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/networkx/readwrite/tests/test_gml.py:443** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/cloudformation/checks/resource/aws/IAMStarActionPolicyDocument.py:50** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/renderer.py:74** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/renderer.py:211** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/renderer.py:273** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/renderer.py:278** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/renderer.py:527** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/evaluate_terraform.py:273** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/evaluate_terraform.py:325** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/evaluate_terraform.py:348** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/evaluate_terraform.py:387** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/safe_eval_functions.py:359** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/safe_eval_functions.py:384** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/safe_eval_functions.py:388** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/variable_rendering/safe_eval_functions.py:391** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/checkov/terraform/graph_builder/graph_components/module.py:87** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/capi_maps.py:157** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/capi_maps.py:295** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/capi_maps.py:451** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:1334** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2301** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2303** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2333** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2355** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2361** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2367** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2374** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2565** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2595** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2673** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2682** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:2950** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:3000** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:3021** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:3052** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py:3510** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/auxfuncs.py:607** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/auxfuncs.py:615** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/auxfuncs.py:619** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:502** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:529** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:623** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:628** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:761** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/format.py:880** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/npyio.py:145** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/npyio.py:331** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1027** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1058** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1060** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1062** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1065** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1070** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/utils.py:1078** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:244** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:246** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:302** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:305** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:789** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:795** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:857** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:859** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:1112** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/hermite_e.py:1391** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/tests/test_public_api.py:470** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/ma/timer_comparison.py:442** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/_internal.py:200** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/arrayprint.py:1463** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_scalarmath.py:616** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_scalarmath.py:642** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_umath_accuracy.py:60** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_umath_accuracy.py:61** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_dtype.py:998** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_records.py:149** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_records.py:150** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_records.py:151** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:239** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:505** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:635** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:696** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:716** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:736** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:762** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:799** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:838** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:890** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_simd.py:1096** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_arrayprint.py:328** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_arrayprint.py:329** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_multiarray.py:1484** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_multiarray.py:3792** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_umath.py:488** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/core/tests/test_umath.py:552** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:81** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:85** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:87** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:122** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:124** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:132** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:139** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:140** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:141** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:239** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:360** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:368** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:425** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:428** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:432** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:435** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:439** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:468** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:470** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/polynomial/tests/test_hermite_e.py:516** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/lib/tests/test_utils.py:125** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/numpy/f2py/tests/test_crackfortran.py:254** - Potential command_injection
  - Pattern matched: Eval(

- **venv/lib/python3.13/site-packages/jsonschema/tests/test_deprecations.py:396** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/dateparser/languages/locale.py:435** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/dateparser/languages/dictionary.py:105** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/blib2to3/pgen2/pgen.py:111** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/blib2to3/pgen2/conv.py:186** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/blib2to3/pgen2/conv.py:212** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/blib2to3/pgen2/literals.py:4** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory_async.py:65** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:128** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:334** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:336** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:364** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:368** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/sklearn/metrics/_ranking.py:1586** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/sklearn/metrics/_ranking.py:1692** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/sklearn/metrics/_ranking.py:1854** - Potential command_injection
  - Pattern matched: eval (

- **venv/lib/python3.13/site-packages/nltk/parse/evaluate.py:62** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/parse/evaluate.py:88** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/parse/transitionparser.py:779** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/parse/transitionparser.py:785** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/tokenize/punkt.py:497** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/tokenize/texttiling.py:451** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/chunk/regexp.py:1306** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/chunk/regexp.py:1396** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/chunk/regexp.py:1405** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/chunk/regexp.py:1412** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/chunk/regexp.py:1422** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/tag/sequential.py:315** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/nltk/corpus/reader/comparative_sents.py:25** - Potential command_injection
  - Pattern matched: eval
   (

- **venv/lib/python3.13/site-packages/litellm/secret_managers/main.py:312** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/secret_managers/aws_secret_manager.py:111** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/caching/caching.py:455** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/caching/qdrant_semantic_cache.py:166** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/caching/s3_cache.py:125** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/caching/redis_semantic_cache.py:179** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/caching/redis_cache.py:672** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/proxy/pass_through_endpoints/pass_through_endpoints.py:146** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/litellm/types/llms/vertex_ai.py:126** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/tests/test_egg_info.py:277** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/tests/namespaces.py:34** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/typing_extensions.py:1215** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/config/expand.py:72** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/packaging/_parser.py:332** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/more_itertools/recipes.py:992** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/more_itertools/recipes.py:999** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/wheel/vendored/packaging/_parser.py:334** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/packaging/licenses/__init__.py:100** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/jaraco/functools/__init__.py:522** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/setuptools/_distutils/compilers/C/base.py:1120** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/differentiate/_differentiate.py:440** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/differentiate/_differentiate.py:486** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_bracket.py:242** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_bracket.py:260** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_bracket.py:648** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_bracket.py:664** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_optimize.py:323** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_chandrupatla.py:154** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_chandrupatla.py:159** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_chandrupatla.py:427** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/_chandrupatla.py:464** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/_elementwise_iterative_method.py:227** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/_elementwise_iterative_method.py:250** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/_continued_fraction.py:325** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/_continued_fraction.py:329** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/_continuous_distns.py:3450** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/_continuous_distns.py:3462** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/integrate/_tanhsinh.py:400** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/integrate/_tanhsinh.py:414** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:343** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:397** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:527** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:570** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:593** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:594** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:608** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:653** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:676** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/_spline_filters.py:677** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_signaltools.py:1716** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_signaltools.py:1734** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:157** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:158** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:162** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:182** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:187** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:191** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:192** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:195** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:214** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/signal/tests/test_bsplines.py:221** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/integrate/tests/test__quad_vec.py:143** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/integrate/_ivp/tests/test_ivp.py:678** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/tests/test_continued_fraction.py:149** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/tests/test_continuous.py:89** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/stats/tests/test_continuous.py:2047** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/main.py:650** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/main.py:697** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/main.py:840** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/main.py:1422** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/main.py:1446** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/problem.py:80** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/problem.py:560** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/problem.py:886** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/problem.py:947** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/_lib/cobyqa/problem.py:1192** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_bsplines.py:123** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_bsplines.py:131** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_bsplines.py:862** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_bsplines.py:1322** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:837** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:1379** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2262** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2268** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2288** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2308** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2512** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2548** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_interpolate.py:2588** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/interpolate/tests/test_polyint.py:788** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:445** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:452** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:559** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:569** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:754** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:761** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:1393** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:1403** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/spatial/tests/test_distance.py:2136** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:44** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:300** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/sparse/csgraph/tests/test_graph_laplacian.py:302** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/tests/test_constraints.py:183** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/optimize/tests/test__differential_evolution.py:260** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/special/tests/test_orthogonal.py:280** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/special/_precompute/wright_bessel.py:183** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/scipy/special/_precompute/wright_bessel.py:203** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pydantic/v1/utils.py:195** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:451** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:484** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/mark/expression.py:178** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/mark/expression.py:227** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/mark/__init__.py:60** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/mark/__init__.py:61** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/_code/code.py:163** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/_code/code.py:172** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/_pytest/_code/code.py:288** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pycparser/ply/yacc.py:1562** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pycparser/ply/cpp.py:600** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_transforms.py:868** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_transforms.py:869** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_transforms.py:873** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_transforms.py:875** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_pickle.py:164** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/tests/test_patches.py:475** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_editor/_formlayout.py:355** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/console.py:213** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:392** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:393** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:138** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:139** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:396** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pygments/formatters/__init__.py:91** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pygments/lexers/foxpro.py:70** - Potential command_injection
  - Pattern matched: EVAL(

- **venv/lib/python3.13/site-packages/pygments/lexers/special.py:115** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pygments/lexers/_julia_builtins.py:150** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/pygments/lexers/_julia_builtins.py:361** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/psutil/tests/test_connections.py:360** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/psutil/tests/test_connections.py:362** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/psutil/tests/test_connections.py:365** - Potential command_injection
  - Pattern matched: eval(

- **venv/lib/python3.13/site-packages/psutil/tests/test_connections.py:367** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:1444** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:3967** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:3972** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:4019** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:4031** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:4036** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:4064** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/skipping.py:87** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/skipping.py:116** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/pytester.py:292** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/isort/literal.py:54** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/packaging/_parser.py:332** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pyparsing/results.py:62** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/flask/cli.py:142** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/flask/cli.py:143** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/flask/cli.py:964** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/coverage/parser.py:662** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/util.py:399** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/util.py:400** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/jinja2/nativetypes.py:40** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/jinja2/lexer.py:663** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/jinja2/nodes.py:581** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/tqdm/cli.py:38** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/typing_extensions.py:1215** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/rich/markup.py:190** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/packaging/_parser.py:332** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/packaging/licenses/__init__.py:100** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/pygments/formatters/__init__.py:91** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:697** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:708** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:745** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:760** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/generativeai/types/content_types.py:829** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/ai/generativelanguage_v1alpha/types/content.py:368** - Potential command_injection
  - Pattern matched: eval (

- **.formatvenv/lib/python3.13/site-packages/google/ai/generativelanguage_v1alpha/types/content.py:408** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/google/ai/generativelanguage_v1beta/types/content.py:368** - Potential command_injection
  - Pattern matched: eval (

- **.formatvenv/lib/python3.13/site-packages/google/ai/generativelanguage_v1beta/types/content.py:408** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/packaging/licenses/__init__.py:100** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/blib2to3/pgen2/pgen.py:111** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/blib2to3/pgen2/conv.py:186** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/blib2to3/pgen2/conv.py:212** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/blib2to3/pgen2/literals.py:4** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pydantic/v1/utils.py:195** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pydantic/_internal/_namespace_utils.py:37** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:623** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:656** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/mark/expression.py:178** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/mark/expression.py:227** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/mark/__init__.py:60** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/mark/__init__.py:61** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_code/code.py:163** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_code/code.py:172** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_code/code.py:288** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/console.py:213** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:392** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/tbtools.py:393** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:138** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:139** - Potential command_injection
  - Pattern matched: eval(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/__init__.py:396** - Potential command_injection
  - Pattern matched: eval(

- **.venv/lib/python3.12/site-packages/pip/_vendor/rich/markup.py:190** - Potential command_injection
  - Pattern matched: eval(

- **.venv/lib/python3.12/site-packages/pip/_vendor/packaging/_parser.py:332** - Potential command_injection
  - Pattern matched: eval(

- **.venv/lib/python3.12/site-packages/pip/_vendor/packaging/licenses/__init__.py:100** - Potential command_injection
  - Pattern matched: eval(

- **.venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/__init__.py:91** - Potential command_injection
  - Pattern matched: eval(

- **tests/test_chatops.py:71** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/typing_extensions.py:1444** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/decorator.py:161** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/six.py:740** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/threadpoolctl.py:1286** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/git/util.py:363** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/git/util.py:380** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/anyio/to_interpreter.py:116** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ephem/__init__.py:92** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/launch.py:32** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/build_meta.py:317** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ply/yacc.py:1984** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ply/yacc.py:3260** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ply/lex.py:215** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ply/lex.py:1036** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pkg_resources/__init__.py:1738** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pkg_resources/__init__.py:1749** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/typing_inspection/typing_objects.py:100** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/typing_inspection/typing_objects.py:132** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/flask/config.py:209** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/prophet/serialize.py:23** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/prophet/__init__.py:13** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/coverage/templite.py:74** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/coverage/execfile.py:211** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/config.py:1895** - Potential command_injection
  - Pattern matched: Exec(

- **venv/lib/python3.13/site-packages/gunicorn/config.py:1901** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/arbiter.py:181** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/arbiter.py:183** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/arbiter.py:301** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/arbiter.py:399** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/arbiter.py:416** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/glogging.py:393** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/glogging.py:400** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/util.py:257** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/jinja2/debug.py:145** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/jinja2/environment.py:1228** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/cffi/setuptools_ext.py:25** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/prometheus_client/decorator.py:195** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_manager.py:111** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_manager.py:120** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_manager.py:464** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_hooks.py:512** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_hooks.py:534** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_hooks.py:573** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pluggy/_hooks.py:580** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/bandit/plugins/exec.py:21** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/safety/tool/tool_inspector.py:217** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/claw/_ast/pep/clawastpep695.py:206** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_decor/wrap/wrapmain.py:87** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_decor/wrap/__init__.py:54** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_decor/wrap/__init__.py:360** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_check/forward/fwdscope.py:210** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_check/code/__init__.py:1388** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/cache/utilcachecall.py:572** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/func/utilfuncmake.py:258** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/func/utilfuncmake.py:259** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/func/utilfuncmake.py:273** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/hint/pep/proposal/pep613.py:111** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/hint/pep/proposal/pep695.py:72** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/hint/pep/proposal/pep695.py:79** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/beartype/_util/hint/pep/proposal/pep695.py:81** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psOperators.py:270** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psOperators.py:341** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psOperators.py:343** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psOperators.py:348** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psLib.py:152** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/misc/psLib.py:159** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/t1Lib/__init__.py:158** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/fontTools/t1Lib/__init__.py:168** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_vendor/pkg_resources/__init__.py:1714** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_vendor/pkg_resources/__init__.py:1725** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_vendor/distlib/scripts.py:163** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_vendor/urllib3/packages/six.py:787** - Potential command_injection
  - Pattern matched: exec (

- **venv/lib/python3.13/site-packages/pip/_vendor/pygments/formatters/__init__.py:103** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_vendor/pygments/lexers/__init__.py:154** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_internal/utils/setuptools_build.py:12** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pip/_internal/utils/setuptools_build.py:46** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pyflakes/test/test_imports.py:680** - Potential command_injection
  - Pattern matched: Exec(

- **venv/lib/python3.13/site-packages/pyflakes/test/test_imports.py:681** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pyflakes/test/test_api.py:398** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/botocore/vendored/six.py:735** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/networkx/utils/decorators.py:915** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/workers/base.py:108** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/workers/base.py:112** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/workers/base.py:113** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/workers/base.py:117** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/gunicorn/workers/sync.py:30** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/prophet/stan_model/cmdstan-2.31.0/stan/lib/stan_math/lib/tbb_2020.3/python/tbb/pool.py:353** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/numpy/testing/_private/utils.py:1119** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/numpy/testing/_private/utils.py:1407** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/numpy/f2py/tests/test_f2py2e.py:779** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/numpy/f2py/tests/test_f2py2e.py:787** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/dateparser/utils/strptime.py:25** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/joblib/test/test_utils.py:8** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/joblib/test/test_memory.py:164** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/joblib/externals/loky/backend/fork_exec.py:12** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/joblib/externals/loky/backend/fork_exec.py:46** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/joblib/externals/loky/backend/popen_loky_posix.py:128** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/sklearn/externals/array_api_compat/cupy/linalg.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/sklearn/externals/array_api_compat/cupy/fft.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/sklearn/externals/array_api_compat/torch/__init__.py:12** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/sklearn/externals/array_api_compat/dask/array/linalg.py:22** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/sklearn/externals/array_api_compat/dask/array/fft.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/nltk/sem/util.py:274** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/tests/test_editable_install.py:449** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/_distutils/core.py:228** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/_distutils/core.py:268** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/_vendor/typing_extensions.py:1215** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/setuptools/tests/config/test_pyprojecttoml.py:98** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/optimize/_nonlin.py:1621** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/decorator.py:166** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/_bunch.py:160** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/stats/_distn_infrastructure.py:368** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/stats/_distn_infrastructure.py:744** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/array_api_compat/cupy/linalg.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/array_api_compat/cupy/fft.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/array_api_compat/torch/__init__.py:12** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/array_api_compat/dask/array/linalg.py:22** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/scipy/_lib/array_api_compat/dask/array/fft.py:6** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:451** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/_pytest/assertion/rewrite.py:186** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/_pytest/_py/path.py:1155** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/_pytest/_py/path.py:1161** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/_pytest/_code/code.py:288** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/ephem/tests/test_usno.py:487** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py:2567** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pycparser/ply/yacc.py:1982** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pycparser/ply/yacc.py:3254** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pycparser/ply/lex.py:215** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pycparser/ply/lex.py:1039** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_compat.py:157** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_compat.py:159** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/backend_qt.py:476** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/backend_qt.py:657** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/sphinxext/plot_directive.py:543** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/sphinxext/plot_directive.py:546** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/sphinxext/plot_directive.py:552** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/sphinxext/plot_directive.py:554** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_editor/_formlayout.py:576** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_editor/_formlayout.py:582** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/matplotlib/backends/qt_editor/_formlayout.py:592** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/werkzeug/routing/rules.py:737** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/werkzeug/debug/console.py:177** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pygments/formatters/__init__.py:103** - Potential command_injection
  - Pattern matched: exec(

- **venv/lib/python3.13/site-packages/pygments/lexers/installers.py:66** - Potential command_injection
  - Pattern matched: Exec(

- **venv/lib/python3.13/site-packages/pygments/lexers/__init__.py:154** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/typing_extensions.py:1444** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/anyio/to_interpreter.py:116** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/typing_inspection/typing_objects.py:100** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/typing_inspection/typing_objects.py:132** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/flask/config.py:189** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/coverage/templite.py:74** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/coverage/execfile.py:211** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/config.py:1876** - Potential command_injection
  - Pattern matched: Exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/config.py:1882** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/arbiter.py:182** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/arbiter.py:184** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/arbiter.py:302** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/arbiter.py:400** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/arbiter.py:417** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/glogging.py:394** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/glogging.py:401** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/util.py:258** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/jinja2/debug.py:145** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/jinja2/environment.py:1228** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/prometheus_client/decorator.py:195** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_manager.py:111** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_manager.py:120** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_manager.py:464** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_hooks.py:512** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_hooks.py:534** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_hooks.py:573** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pluggy/_hooks.py:580** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/typing_extensions.py:1215** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/pkg_resources/__init__.py:1714** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/pkg_resources/__init__.py:1725** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/distlib/scripts.py:163** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/urllib3/packages/six.py:787** - Potential command_injection
  - Pattern matched: exec (

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/pygments/formatters/__init__.py:103** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_vendor/pygments/lexers/__init__.py:154** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_internal/utils/setuptools_build.py:10** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pip/_internal/utils/setuptools_build.py:43** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pyflakes/test/test_imports.py:680** - Potential command_injection
  - Pattern matched: Exec(

- **.formatvenv/lib/python3.13/site-packages/pyflakes/test/test_imports.py:681** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pyflakes/test/test_api.py:398** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/workers/base.py:107** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/workers/base.py:111** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/workers/base.py:112** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/workers/base.py:116** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/gunicorn/workers/sync.py:31** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/pydantic/_internal/_typing_extra.py:623** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/_pytest/assertion/rewrite.py:186** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_py/path.py:1155** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_py/path.py:1161** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/_pytest/_code/code.py:288** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/anyio/_backends/_asyncio.py:2567** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/routing/rules.py:737** - Potential command_injection
  - Pattern matched: exec(

- **.formatvenv/lib/python3.13/site-packages/werkzeug/debug/console.py:177** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:1714** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:1725** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_vendor/distlib/scripts.py:163** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/six.py:787** - Potential command_injection
  - Pattern matched: exec (

- **.venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/__init__.py:103** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/__init__.py:154** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_internal/utils/setuptools_build.py:12** - Potential command_injection
  - Pattern matched: exec(

- **.venv/lib/python3.12/site-packages/pip/_internal/utils/setuptools_build.py:46** - Potential command_injection
  - Pattern matched: exec(

- **.env:N/A** - Potential hardcoded secret
  - Long value detected, ensure no secrets are committed

- **terraform/main.tf:N/A** - Unencrypted storage
  - Storage volumes should be encrypted

## 📋 Recommendations

- **HIGH**: Address within 24 hours
  - Fix 3 high-priority security issues

- **MEDIUM**: Address within 1 week
  - Review and fix 1416 medium-priority issues

- **GENERAL**: Security review required
  - Conduct comprehensive security review before production deployment

## 📊 Detailed Results

### Dependency Scan
```json
{}
```

### Code Security Scan
```json
{}
```

### Configuration Security
```json
{}
```

### Infrastructure Security
```json
{}
```

---

**Note**: This report was generated automatically. Please review all findings and address critical and high-priority issues before production deployment.
