# OpenAI API Cost Estimates

This document provides cost estimates for processing meeting recordings with the Meeting Notes Processor.

## Pricing (as of November 2025)

### Whisper API (Transcription)
- **Rate:** $0.006 per minute of audio
- **Model:** whisper-1

### GPT-4 Turbo (Analysis)
- **Input tokens:** $0.01 per 1K tokens
- **Output tokens:** $0.03 per 1K tokens
- **Model:** gpt-4-turbo-preview

## Example Cost Breakdowns

### Example 1: 15-Minute Daily Standup

**Audio:**
- Duration: 15 minutes
- Transcription cost: 15 × $0.006 = **$0.09**

**Analysis:**
- Transcript length: ~2,250 words (~3,000 tokens)
- Input tokens: 3,000
- Output tokens: ~300 (summary, action items)
- Analysis cost: (3 × $0.01) + (0.3 × $0.03) = $0.03 + $0.009 = **$0.039**

**Total: $0.129 (~$0.13)**

### Example 2: 45-Minute Sprint Planning

**Audio:**
- Duration: 45 minutes
- Transcription cost: 45 × $0.006 = **$0.27**

**Analysis:**
- Transcript length: ~6,750 words (~9,000 tokens)
- Input tokens: 9,000
- Output tokens: ~600 (detailed summary, multiple action items, decisions)
- Analysis cost: (9 × $0.01) + (0.6 × $0.03) = $0.09 + $0.018 = **$0.108**

**Total: $0.378 (~$0.38)**

### Example 3: 2-Hour All-Hands Meeting

**Audio:**
- Duration: 120 minutes
- Transcription cost: 120 × $0.006 = **$0.72**

**Analysis:**
- Transcript length: ~18,000 words (~24,000 tokens)
- Chunked processing (2 chunks)
- Input tokens: 24,000
- Output tokens: ~1,000
- Analysis cost: (24 × $0.01) + (1.0 × $0.03) = $0.24 + $0.03 = **$0.27**

**Total: $0.99 (~$1.00)**

### Example 4: 30-Minute 1:1 Meeting

**Audio:**
- Duration: 30 minutes
- Transcription cost: 30 × $0.006 = **$0.18**

**Analysis:**
- Transcript length: ~4,500 words (~6,000 tokens)
- Input tokens: 6,000
- Output tokens: ~400
- Analysis cost: (6 × $0.01) + (0.4 × $0.03) = $0.06 + $0.012 = **$0.072**

**Total: $0.252 (~$0.25)**

## Monthly Cost Estimates

### Scenario 1: Small Team (5-10 people)
- 5 daily standups/week (15 min each): 5 × $0.13 × 4 = **$2.60/month**
- 2 planning meetings/month (45 min each): 2 × $0.38 = **$0.76/month**
- 4 1:1s/month (30 min each): 4 × $0.25 = **$1.00/month**

**Total: ~$4.36/month**

### Scenario 2: Medium Team (20-50 people)
- 5 standups/week: **$2.60/month**
- 4 planning meetings/month: 4 × $0.38 = **$1.52/month**
- 10 1:1s/month: 10 × $0.25 = **$2.50/month**
- 2 all-hands/month (2 hours): 2 × $1.00 = **$2.00/month**
- 8 design reviews/month (45 min): 8 × $0.38 = **$3.04/month**

**Total: ~$11.66/month**

### Scenario 3: Heavy Usage (100+ people)
- 5 standups/week (multiple teams): **$10.40/month**
- 8 planning meetings/month: 8 × $0.38 = **$3.04/month**
- 30 1:1s/month: 30 × $0.25 = **$7.50/month**
- 4 all-hands/month: 4 × $1.00 = **$4.00/month**
- 20 misc meetings/month: 20 × $0.38 = **$7.60/month**

**Total: ~$32.54/month**

## Cost Optimization Tips

### 1. Pre-process Audio Files
Reduce file size before uploading:
```bash
# Compress to mono, 16kHz, 64kbps
ffmpeg -i input.mp3 -ar 16000 -ac 1 -ab 64k output.mp3
```
This typically reduces files by 50-70% with minimal quality loss for speech.

### 2. Selective Processing
Don't process every meeting:
- Skip routine standups that follow the same pattern
- Focus on planning, decision-making, and brainstorming sessions
- Process only meetings with action items

### 3. Use GPT-3.5 for Simple Meetings
For straightforward meetings (standups, status updates), use GPT-3.5-turbo:
- Input: $0.0005 per 1K tokens (50% cheaper)
- Output: $0.0015 per 1K tokens (50% cheaper)
- Saves ~$0.05 per meeting

### 4. Batch Processing
Process multiple recordings together:
- Reduced overhead
- Better rate limiting management
- Can negotiate volume discounts with OpenAI

### 5. Smart Transcript Chunking
Only send relevant parts to GPT-4:
- Detect and skip long silences
- Remove filler words and repetitions
- Focus on sections with decisions/action items

## Cost Comparison

### Manual Note-Taking
**Time cost:**
- 1 hour meeting = ~30 minutes to write good notes
- If hourly rate is $50: $25 per meeting
- 10 meetings/month: **$250/month**

**Meeting Notes Processor:**
- 10 meetings/month: ~**$5/month**
- Time saved: 5 hours/month
- **ROI: 50x**

### Professional Transcription Services
Services like Rev.com or Otter.ai:
- Rev.com: $1.50/minute = $90 for 1-hour meeting
- Otter.ai: $20/month for 6,000 minutes

**Meeting Notes Processor:**
- More affordable for most use cases
- Higher quality analysis (action items, decisions)
- Full control and customization

## Reducing Costs Further

### Use Caching
Process the same recording once:
- Cache transcripts locally
- Re-analyze with different prompts without re-transcribing
- Save ~60% on repeated processing

### Adjust Analysis Depth
Configure what to extract:
```yaml
# Minimal (cheap): Just summary + action items
extract_summary: true
extract_action_items: true
extract_decisions: false
extract_key_topics: false

# Full (comprehensive): Everything
extract_summary: true
extract_action_items: true
extract_decisions: true
extract_key_topics: true
extract_attendees: true
```

Minimal config saves ~40% on analysis costs.

## Sample Monthly Invoice

For a team processing **20 meetings/month** (mix of sizes):

| Meeting Type | Count | Duration | Per Meeting | Subtotal |
|--------------|-------|----------|-------------|----------|
| Standups | 8 | 15 min | $0.13 | $1.04 |
| Planning | 4 | 45 min | $0.38 | $1.52 |
| 1:1s | 6 | 30 min | $0.25 | $1.50 |
| Design Reviews | 2 | 45 min | $0.38 | $0.76 |

**Total: $4.82/month**

**Annual: ~$58**

**Per person (10-person team): ~$5.80/year**

## Conclusion

The Meeting Notes Processor is extremely cost-effective:
- **Individual user:** <$2/month
- **Small team:** ~$5/month
- **Large org:** ~$30-50/month

Compare this to:
- Manual note-taking time: Worth hundreds of dollars
- Professional services: $20-100+/month
- Lost context/action items: Priceless

The tool pays for itself if it saves you **just 10 minutes per month**!
