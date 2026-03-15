from agentflow import DAG, codex, codex_fuzz_campaign


with DAG(
    "airflow-like-fuzz-dual-campaigns-128",
    description=(
        "Python-authored dual 64-shard Codex fuzz campaigns that share one DAG and one maintainer merge "
        "for a combined 128 workers."
    ),
    working_dir="./codex_fuzz_python_dual_campaigns_128",
    concurrency=48,
    fail_fast=True,
) as dag:
    browser = codex_fuzz_campaign(
        preset="browser-surface",
        shards=64,
        layout="batched",
        batch_size=8,
        campaign_label="browser-surface",
        task_prefix="browser",
    )
    protocol = codex_fuzz_campaign(
        preset="protocol-stack",
        shards=64,
        layout="grouped",
        campaign_label="protocol-stack",
        task_prefix="protocol",
    )
    maintainer_merge = codex(
        task_id="maintainer_merge",
        model="gpt-5-codex",
        tools="read_only",
        timeout_seconds=300,
        prompt=(
            "Compare these two coordinated campaigns and produce one maintainer release brief.\n\n"
            "Browser campaign:\n"
            "{{ nodes.browser_merge.output }}\n\n"
            "Protocol campaign:\n"
            "{{ nodes.protocol_merge.output }}"
        ),
    )

    [browser.merge, protocol.merge] >> maintainer_merge

print(dag.to_yaml(), end="")
