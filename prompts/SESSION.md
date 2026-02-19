# General Guidelines

{{ system_prompt }}

# Party Members

{% for p in party_summaries %}
  - {{ p }}
{% end %}

# Campaign Summary

{{ campaign_summary }}

{% if previous_session_summary is not None %}
  # Previous Session

  {{ previous_session_summary }}
{% end %}

# Session Plan

{{ session_plan }}