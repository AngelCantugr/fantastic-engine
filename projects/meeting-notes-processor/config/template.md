# {{meeting_title}} - {{meeting_date}}

**Meeting Type:** {{meeting_type}}
**Date:** {{meeting_date}}
**Duration:** {{duration}}
**Attendees:** {{attendees}}

## 📋 Summary

{{ai_summary}}

**Key Outcomes:**
{{key_outcomes}}

## ✅ Action Items

{{action_items}}

## 🎯 Decisions Made

{{decisions}}

## 💡 Key Topics Discussed

{{key_topics}}

{% if include_transcript %}
## 📝 Full Transcript

<details>
<summary>Click to expand full transcript</summary>

{{full_transcript}}

</details>
{% endif %}

{% if timestamps %}
## 🔗 Timestamps

Quick navigation to key moments:
{{timestamps}}
{% endif %}

---

*Meeting notes generated on {{generation_date}} at {{generation_time}}*
{% if processing_stats %}
*Processing time: {{processing_time}} | Cost: ${{processing_cost}}*
{% endif %}
