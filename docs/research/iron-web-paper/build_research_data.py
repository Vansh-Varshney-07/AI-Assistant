"""Build source-labelled research tables; these are not Iron Web experiments."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-10-24"


def csv_file(name, fields, rows):
    with (ROOT / name).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


# Metadata for additional papers was checked on their primary arXiv records.
# Year is first preprint year; note records the particular version inspected.
papers = [
    ("dey2026spatial", "Spatial Metaphors for LLM Memory: A Critical Analysis of the MemPalace Architecture", "Robin Dey and Panyanon Viradecha", "2026", "2604.21284", "v1", "cs.AI", "supplied PDF methods/results/references; principal tables visually checked", "seed paper", "raw storage; benchmark attribution; metaphor versus mechanism"),
    ("chhikara2025mem0", "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory", "Prateek Chhikara and Dev Khant and Saket Aryan and Taranjeet Singh and Deshraj Yadav", "2025", "2504.19413", "v1", "cs.CL", "supplied PDF methods/results/references; principal tables visually checked", "seed paper", "incremental extraction; update operations; graph variant; LoCoMo"),
    ("rasmussen2025zep", "Zep: A Temporal Knowledge Graph Architecture for Agent Memory", "Preston Rasmussen and Pavlo Paliychuk and Travis Beauvais and Jack Ryan and Daniel Chalef", "2025", "2501.13956", "v1", "cs.CL", "supplied PDF methods/results/references; principal tables visually checked", "seed paper", "temporal graph; raw episodes; provenance; DMR; LongMemEval"),
    ("wu2024longmemeval", "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory", "Di Wu and Hongwei Wang and Wenhao Yu and Yuwei Zhang and Kai-Wei Chang and Dong Yu", "2024", "2410.10813", "v2", "cs.CL", "primary abstract and metadata; official repository documentation", "cited in Zep and MemPalace analysis", "core benchmark; updates; temporal reasoning; abstention"),
    ("maharana2024locomo", "Evaluating Very Long-Term Conversational Memory of LLM Agents", "Adyasha Maharana and Dong-Ho Lee and Sergey Tulyakov and Mohit Bansal and Francesco Barbieri and Yuwei Fang", "2024", "2402.17753", "", "cs.CL", "primary project page; official README; ACL venue record", "cited in Mem0; discussed in MemPalace analysis", "conversation QA; session evidence; category policy"),
    ("packer2023memgpt", "MemGPT: Towards LLMs as Operating Systems", "Charles Packer and Sarah Wooders and Kevin Lin and Vivian Fang and Shishir G. Patil and Ion Stoica and Joseph E. Gonzalez", "2023", "2310.08560", "v2", "cs.AI", "primary abstract and metadata", "cited in all three seeds", "memory tiers; context management; DMR origin"),
    ("zhong2023memorybank", "MemoryBank: Enhancing Large Language Models with Long-Term Memory", "Wanjun Zhong and Lianghong Guo and Qiqi Gao and He Ye and Yanlin Wang", "2023", "2305.10250", "v3", "cs.CL", "primary abstract and metadata", "cited in Mem0", "forgetting and reinforcement; personalization"),
    ("xu2025amem", "A-MEM: Agentic Memory for LLM Agents", "Wujiang Xu and Zujie Liang and Kai Mei and Hang Gao and Juntao Tan and Yongfeng Zhang", "2025", "2502.12110", "v11", "cs.CL", "primary abstract and metadata", "cited in Mem0", "linked notes; memory evolution; baseline"),
    ("lee2024readagent", "A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts", "Kuang-Huei Lee and Xinyun Chen and Hiroki Furuta and John Canny and Ian Fischer", "2024", "2402.09727", "v3", "cs.CL", "primary abstract and metadata", "cited in Mem0", "gist memory plus source lookup"),
    ("sarthi2024raptor", "RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval", "Parth Sarthi and Salman Abdullah and Aditi Tuli and Shubh Khanna and Anna Goldie and Christopher D. Manning", "2024", "2401.18059", "v1", "cs.CL", "primary abstract and metadata", "cited in Mem0", "hierarchical summaries and retrieval"),
    ("edge2024graphrag", "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", "Darren Edge and Ha Trinh and Newman Cheng and Joshua Bradley and Alex Chao and Apurva Mody and Steven Truitt and Dasha Metropolitansky and Robert Osazuwa Ness and Jonathan Larson", "2024", "2404.16130", "v2", "cs.CL", "primary abstract and metadata", "cited in Zep", "community graph summaries; global queries"),
    ("guo2024lightrag", "LightRAG: Simple and Fast Retrieval-Augmented Generation", "Zirui Guo and Lianghao Xia and Yanhua Yu and Tu Ao and Chao Huang", "2024", "2410.05779", "v3", "cs.IR", "primary abstract and metadata", "cited in Zep", "graph/vector retrieval; incremental updates"),
    ("anokhin2024arigraph", "AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents", "Petr Anokhin and Nikita Semenov and Artyom Sorokin and Dmitry Evseev and Andrey Kravchenko and Mikhail Burtsev and Evgeny Burnaev", "2024", "2407.04363", "v3", "cs.AI", "primary abstract and metadata", "cited in Zep", "episodic-semantic graph prior art"),
    ("lewis2020rag", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "Patrick Lewis and Ethan Perez and Aleksandra Piktus and Fabio Petroni and Vladimir Karpukhin and Naman Goyal and Heinrich Küttler and Mike Lewis and Wen-tau Yih and Tim Rocktäschel and Sebastian Riedel and Douwe Kiela", "2020", "2005.11401", "v4", "cs.CL", "primary abstract and metadata", "cited in MemPalace analysis", "retrieval-conditioned generation foundation"),
    ("shinn2023reflexion", "Reflexion: Language Agents with Verbal Reinforcement Learning", "Noah Shinn and Federico Cassano and Edward Berman and Ashwin Gopinath and Karthik Narasimhan and Shunyu Yao", "2023", "2303.11366", "v4", "cs.AI", "primary abstract and metadata", "cited in Mem0 and Zep", "persistent feedback versus factual memory"),
    ("latimer2025hindsight", "Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects", "Chris Latimer and Nicoló Boschi and Andrew Neeser and Chris Bartholomew and Gaurav Srivastava and Xuan Wang and Naren Ramakrishnan", "2025", "2512.12818", "v1", "cs.CL", "primary abstract and metadata", "Hindsight project cited in MemPalace analysis; exact paper resolved separately", "evidence versus beliefs; structured retain/recall/reflect"),
    ("wu2026longmemevalv2", "LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues", "Di Wu and Zixiang Ji and Asmi Kawatkar and Bryan Kwan and Jia-Chen Gu and Nanyun Peng and Kai-Wei Chang", "2026", "2605.12493", "v1", "cs.CL", "primary abstract and metadata; official project announcement", "newer than seed papers; supplemental", "agent environment experience; workflows; changing state"),
]

catalog = []
bib = []
for key, title, author, year, eprint, version, primary, depth, found, relevance in papers:
    url = f"https://arxiv.org/abs/{eprint}{version}"
    catalog.append(dict(citation_key=key, title=title, authors=author, year=year,
                        version=version, url=url, discovery_path=found, reading_depth=depth,
                        relevance=relevance, verification="primary identity checked; external results not reproduced", accessed=DATE))
    bib.append(f"@misc{{{key},\n  title = {{{{{title}}}}},\n  author = {{{author}}},\n  year = {{{year}}},\n  eprint = {{{eprint}{version}}},\n  archivePrefix = {{arXiv}},\n  primaryClass = {{{primary}}},\n  url = {{{url}}},\n  note = {{Version {version or 'not pinned'}; primary record checked {DATE}; full-text review depth recorded in reference-catalog.csv}}\n}}")

projects = [
    ("mempalace2026benchmarks", "MemPal Benchmark Results — Full Progression", "{MemPalace contributors}", "https://github.com/MemPalace/mempalace/blob/main/benchmarks/BENCHMARKS.md", "MemPalace analysis and issue #29", "project benchmark documentation read", "primary project report; internally inconsistent historical descriptions; pin commit before experiments"),
    ("dial4812026audit", "Multiple issues with benchmark methodology and scoring", "{dial481}", "https://github.com/MemPalace/mempalace/issues/29", "cited in MemPalace analysis", "issue and maintainer response read", "firsthand methodology discussion; critic discloses competing project; not independent reproduction by us"),
    ("yadav2026temporal", "The Token-Efficient Memory Algorithm Now Has Temporal Reasoning", "Deshraj Yadav", "https://mem0.ai/blog/the-token-efficient-memory-algorithm-now-has-temporal-reasoning", "supplemental primary-source update", "primary vendor report screened", "May 14 2026 update; not the supplied 2025 algorithm; top_200 configuration must be resolved"),
    ("barnes2026observational", "Observational Memory: 95% on LongMemEval", "Tyler Barnes", "https://mastra.ai/research/observational-memory", "Mastra project cited in MemPalace analysis", "primary research report screened", "February 9 2026 vendor report; different readers yield different results"),
]
for key, title, author, url, found, depth, verification in projects:
    catalog.append(dict(citation_key=key, title=title, authors=author, year="2026", version="live page; unpinned",
                        url=url, discovery_path=found, reading_depth=depth, relevance="benchmark methodology and score provenance",
                        verification=verification, accessed=DATE))
    bib.append(f"@misc{{{key},\n  title = {{{{{title}}}}},\n  author = {{{author}}},\n  year = {{2026}},\n  url = {{{url}}},\n  note = {{Project report/discussion; accessed {DATE}; not peer-reviewed evidence or a reproduced experiment}}\n}}")

csv_file("reference-catalog.csv", list(catalog[0]), catalog)
(ROOT / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")

overall = []


def result(group, system, dataset, metric, score, source, location, *, std="", model="", k="", chunk="", tokens="", sp50="", sp95="", tp50="", tp95="", latency="", notes="", status="reported; not reproduced"):
    overall.append(dict(comparison_group=group, system=system, dataset=dataset, metric=metric,
                        score_percent=score, std_percentage_points=std, answer_model=model,
                        retrieval_k=k, chunk_tokens=chunk, context_tokens=tokens,
                        search_p50_seconds=sp50, search_p95_seconds=sp95,
                        total_p50_seconds=tp50, total_p95_seconds=tp95,
                        source_latency_seconds_unspecified_quantile=latency,
                        citation_key=source, source_location=location, status=status, notes=notes))


rag_rows = [
    (1,128,.281,.823,.774,1.825,47.77,.23), (1,256,.251,.710,.745,1.628,50.15,.16),
    (1,512,.240,.639,.772,1.710,46.05,.14), (1,1024,.240,.723,.821,1.957,40.74,.17),
    (1,2048,.255,.752,.996,2.182,37.93,.12), (1,4096,.254,.719,1.093,2.711,36.84,.17),
    (1,8192,.279,.838,1.396,4.416,44.53,.13), (2,128,.267,.624,.766,1.829,59.56,.19),
    (2,256,.255,.699,.802,1.907,60.97,.20), (2,512,.247,.746,.829,1.729,58.19,.18),
    (2,1024,.238,.702,.860,1.850,50.68,.13), (2,2048,.261,.829,1.101,2.791,48.57,.22),
    (2,4096,.266,.944,1.451,4.822,51.79,.15), (2,8192,.288,1.124,2.312,9.942,60.53,.16),
]
for k, chunk, a,b,c,d,score,std in rag_rows:
    result("mem0_2025_table2", "RAG", "LoCoMo; adversarial excluded", "overall LLM judge correctness", score,
           "chhikara2025mem0", "p.11 Table 2", std=std, model="gpt-4o-mini protocol; verify exact snapshot", k=k, chunk=chunk,
           tokens=k*chunk, sp50=a,sp95=b,tp50=c,tp95=d, notes="Context is nominal k*chunk size; paper reports chunk size, not an independently measured context average for each RAG row")
memory_rows = [
    ("Full-context",26031,"","",9.870,17.117,72.90,.19),
    ("A-Mem",2520,.668,1.485,1.410,4.374,48.38,.15),
    ("LangMem",127,17.99,59.82,18.53,60.40,58.10,.21),
    ("Zep",3911,.513,.778,1.292,2.926,65.99,.16),
    ("OpenAI ChatGPT memory baseline",4437,"","",.466,.889,52.90,.14),
    ("Mem0",1764,.148,.200,.708,1.440,66.88,.15),
    ("Mem0g",3616,.476,.657,1.091,2.590,68.44,.17),
]
for name,tokens,a,b,c,d,score,std in memory_rows:
    result("mem0_2025_table2", name, "LoCoMo; adversarial excluded", "overall LLM judge correctness", score,
           "chhikara2025mem0", "p.11 Table 2", std=std,model="gpt-4o-mini protocol; provider baseline may differ",tokens=tokens,sp50=a,sp95=b,tp50=c,tp95=d,
           notes="10-run mean +/- SD per paper; provider state and ingestion readiness matter; context tokens are not total lifecycle token cost")

dmr = [("Recursive summarization","gpt-4-turbo",35.3,True), ("Conversation summaries","gpt-4-turbo",78.6,False),
       ("MemGPT","gpt-4-turbo",93.4,True), ("Full-conversation","gpt-4-turbo",94.4,False),
       ("Zep","gpt-4-turbo",94.8,False), ("Conversation summaries","gpt-4o-mini",88.0,False),
       ("Full-conversation","gpt-4o-mini",98.0,False), ("Zep","gpt-4o-mini",98.2,False)]
for name,model,score,prior in dmr:
    result("zep_2025_dmr_"+model,name,"DMR; 500 conversations","QA correctness",score,"rasmussen2025zep","p.6 Table 1",model=model,
           k=10 if name=="Zep" else "", notes="Imported from MemGPT paper" if prior else "Zep study report; short histories; no independent reproduction")

for name,model,score,latency,tokens,iqr in [("Full-context","gpt-4o-mini",55.4,31.3,115000,8.76),("Zep","gpt-4o-mini",63.8,3.20,1600,1.31),
                                         ("Full-context","gpt-4o",60.2,28.9,115000,6.01),("Zep","gpt-4o",71.2,2.58,1600,.684)]:
    result("zep_2025_lme_"+model,name,"LongMemEval_S; historical release","QA correctness",score,"rasmussen2025zep","p.7 Table 2",
           model=model,k=20 if name=="Zep" else "",tokens=tokens,latency=latency,
           notes=f"Context tokens approximate; source latency IQR={iqr}s; latency column not labelled p95; 2024/2025 experimental setup")

mp=[("raw ChromaDB", "LongMemEval", "recall_any@5",96.6,5,"p.9 Table 4; p.10 Table 5","no LLM; historical user-turn-only session indexing described by audit"),
    ("hybrid v4 held-out", "LongMemEval; 450-question subset", "retrieval R@5 as labelled",98.4,5,"p.9 Table 4","source labels LLM required; current benchmark document describes no-rerank run; split provenance disputed"),
    ("AAAK compression", "LongMemEval", "retrieval R@5 as labelled",84.2,5,"p.9 Table 4","lossy representation; not QA accuracy"),
    ("room boosting", "LongMemEval", "retrieval R@5 as labelled",89.4,5,"p.9 Table 4","metadata-filtered variant; not the maintainer's later room QA score"),
    ("raw", "LoCoMo; subset policy must be checked", "retrieval R@10 as labelled",60.3,10,"p.10 Table 5","not QA accuracy"),
    ("hybrid", "LoCoMo; subset policy must be checked", "retrieval R@10 as labelled",88.9,10,"p.10 Table 5","paper says LLM reranking; project documentation identifies no-LLM hybrid v5; unresolved cross-source labelling"),
    ("configuration unclear in Table 5", "LongMemEval", "approximate QA accuracy",67.2,"","p.10 Table 5","quarantine from comparative ranking; maintainer distinguishes raw 66.8 and rooms 67.2")]
for name,ds,metric,score,k,loc,note in mp:
    result("mempalace_historical_context_only", "MemPalace "+name,ds,metric,score,"dey2026spatial",loc,k=k,notes=note,
           status="secondary report; verify primary configuration before comparison")
for name,score in [("raw",66.8),("rooms",67.2),("aaak",53.2)]:
    result("mempalace_maintainer_qa_context_only","MemPalace "+name,"LongMemEval; run sample/config not checked","QA accuracy",score,
           "dial4812026audit","maintainer comment 2026-04-09; issuecomment-4215697566",notes="historical maintainer report; not reproduced; do not rank against unmatched protocols")
result("hindsight_abstract_context_only","Hindsight","LongMemEval","overall accuracy",91.4,"latimer2025hindsight","abstract",
       notes="primary abstract screening; model/settings and full-text result table still need extraction")
result("mastra_2026_context_only","Mastra OM","LongMemEval","overall answer score",94.87,"barnes2026observational","research report",model="gpt-5-mini",
       notes="vendor-reported; not R@5; different reader from 2025 studies; no reproduction")
result("mem0_may2026_context_only","Mem0 updated token-efficient algorithm","LongMemEval; 500 questions per report","overall score",94.4,"yadav2026temporal","May 14 2026 report",
       notes="vendor report labels overall top_200 setting and <7000-token retrieval budget; clarify top_200 semantics/reader/judge before comparison; not 2025 Mem0")
csv_file("reported-results.csv", list(overall[0]), overall)

categories=[]
# Columns in each tuple: F1, BLEU-1, judge mean, judge SD, repeated in
# single-hop / multi-hop / open-domain / temporal order (Mem0 Table 1).
table1={
    "LoCoMo":[(25.02,19.75,None,None),(12.04,11.16,None,None),(40.36,29.05,None,None),(18.41,14.77,None,None)],
    "ReadAgent":[(9.15,6.48,None,None),(5.31,5.12,None,None),(9.67,7.66,None,None),(12.60,8.87,None,None)],
    "MemoryBank":[(5.00,4.77,None,None),(5.56,5.94,None,None),(6.61,5.16,None,None),(9.68,6.99,None,None)],
    "MemGPT":[(26.65,17.72,None,None),(9.15,7.44,None,None),(41.04,34.34,None,None),(25.52,19.44,None,None)],
    "A-Mem (prior)": [(27.02,20.09,None,None),(12.14,12.00,None,None),(44.65,37.06,None,None),(45.85,36.67,None,None)],
    "A-Mem (authors rerun)": [(20.76,14.90,39.79,.38),(9.22,8.81,18.85,.31),(33.34,27.58,54.05,.22),(35.40,31.08,49.91,.31)],
    "LangMem": [(35.51,26.86,62.23,.75),(26.04,22.32,47.92,.47),(40.91,33.63,71.12,.20),(30.75,25.84,23.43,.39)],
    "Zep": [(35.74,23.30,61.70,.32),(19.37,14.82,41.35,.48),(49.56,38.92,76.60,.13),(42.00,34.53,49.31,.50)],
    "OpenAI": [(34.30,23.72,63.79,.46),(20.09,15.42,42.92,.63),(39.31,31.16,62.29,.12),(14.04,11.25,21.71,.20)],
    "Mem0": [(38.72,27.13,67.13,.65),(28.64,21.58,51.15,.31),(47.65,38.72,72.93,.11),(48.93,40.51,55.51,.34)],
    "Mem0g": [(38.09,26.03,65.71,.45),(24.32,18.82,47.19,.67),(49.27,40.30,75.71,.21),(51.55,40.28,58.13,.44)],
}
for system,values in table1.items():
    for category,(f1,bleu,judge,std) in zip(["single-hop","multi-hop","open-domain","temporal"],values):
        categories.append(dict(comparison_group="mem0_2025_table1",dataset="LoCoMo; adversarial excluded",system=system,
                               answer_model="see baseline-specific protocol",category=category,f1_percent=f1,bleu1_percent=bleu,
                               judge_correct_percent=judge,judge_std_percentage_points=std,citation_key="chhikara2025mem0",
                               source_location="p.9 Table 1",notes="Prior rows lack judge scores; not zero; table mixes imported results and authors' runs"))
zep_cat=[("single-session-preference",30.0,53.3,20.0,56.7), ("single-session-assistant",81.8,75.0,94.6,80.4),
         ("temporal-reasoning",36.5,54.1,45.1,62.4), ("multi-session",40.6,47.4,44.3,57.9),
         ("knowledge-update",76.9,74.4,78.2,83.3), ("single-session-user",81.4,92.9,81.4,92.9)]
for category,a,b,c,d in zep_cat:
    for model,full,zep in [("gpt-4o-mini",a,b),("gpt-4o",c,d)]:
        for system,score in [("Full-context",full),("Zep",zep)]:
            categories.append(dict(comparison_group="zep_2025_table3_"+model,dataset="LongMemEval_S; historical release",system=system,
                                   answer_model=model,category=category,f1_percent="",bleu1_percent="",judge_correct_percent=score,
                                   judge_std_percentage_points="",citation_key="rasmussen2025zep",source_location="p.7 Table 3",
                                   notes="Table's relative deltas omitted; recompute from displayed values if needed"))
csv_file("reported-category-results.csv", list(categories[0]), categories)

reference_sections=[]
for paper in ["2604.21284v1","2504.19413v1","2501.13956v1"]:
    text=(ROOT/"extracted"/f"{paper}.txt").read_text(encoding="utf-8")
    match=re.search(r"(?m)^\s*References\s*$",text)
    if not match:
        raise ValueError(f"No reference heading found: {paper}")
    section=text[match.end():]
    cutoff=re.search(r"(?m)^\s*Appendix(?:\s+[A-Z].*)?\s*$",section)
    if cutoff:
        section=section[:cutoff.start()]
    reference_sections.append(f"===== {paper}: extracted reference section; unverified discovery text =====\n"+section.strip())
(ROOT/"cited-reference-lists.txt").write_text("\n\n".join(reference_sections)+"\n",encoding="utf-8")

log={"prepared":DATE,"scope":"pre-manuscript research for Iron Web; supplied format pending",
     "supplied_pdf_count":3,"supplied_pdf_pages":55,"curated_reference_count":len(catalog),
     "reported_overall_rows":len(overall),"reported_category_rows":len(categories),
     "pdf_tables_visually_checked":["Mem0 Tables 1 and 2","Zep Tables 1, 2 and 3","MemPalace Tables 4, 5 and 6"],
     "external_results_reproduced":False,"iron_web_public_benchmark_results":"not measured",
     "new_application_tests_run":False,"application_code_modified":False,
     "limitations":["Targeted reference expansion, not exhaustive systematic review",
                    "Additional papers mostly abstract/metadata screened, not full-text reviewed",
                    "PDF extraction warned about rotated text and overlapping layout",
                    "Historical and live primary reports may use different dataset/model versions",
                    "Gemini deep-research skill runtime unavailable: GEMINI_API_KEY not configured; used direct PDF and primary-source tools"],
     "arithmetic_from_rounded_tables":{
         "mem0_vs_chatgpt_relative_percent":(66.88/52.90-1)*100,
         "mem0_vs_chatgpt_percentage_points":66.88-52.90,
         "mem0g_vs_mem0_relative_percent":(68.44/66.88-1)*100,
         "mem0g_vs_mem0_percentage_points":68.44-66.88,
         "mem0_p95_reduction_vs_fullcontext_percent":(1-1.440/17.117)*100,
         "mem0_context_token_reduction_percent":(1-1764/26031)*100,
         "zep_mini_relative_percent":(63.8/55.4-1)*100,
         "zep_4o_relative_percent":(71.2/60.2-1)*100,
     }}
(ROOT/"research-log.json").write_text(json.dumps(log,indent=2),encoding="utf-8")
print(json.dumps({"references":len(catalog),"overall_rows":len(overall),"category_rows":len(categories)},indent=2))
