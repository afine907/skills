# 客服 Agent 长对话退化监控方案

## 问题诊断

长对话（20+ 轮）中出现的两个核心症状：

1. **上下文遗忘**：Agent 忘记之前对话中已确认的信息
2. **重复提问**：Agent 重复询问用户已经回答过的问题

根因通常是：
- 上下文窗口超出 LLM 有效处理长度，导致关键信息被截断或"淹没"
- 对话摘要/压缩策略丢失关键事实
- 缺乏对话状态追踪机制
- 没有运行时监控来检测退化行为

---

## 整体架构

```
用户消息 → [对话状态管理器] → [Agent] → [响应质量检测器] → 用户回复
                ↑                    ↓
           [状态存储]          [监控指标采集]
                ↑                    ↓
           [检索增强]          [告警 & 仪表盘]
```

监控方案分为三层：

| 层级 | 目标 | 延迟要求 |
|------|------|----------|
| **L1: 实时检测** | 在响应返回用户前拦截退化响应 | < 200ms |
| **L2: 近实时监控** | 对话结束后立即评估会话质量 | < 30s |
| **L3: 离线分析** | 批量分析历史会话，发现系统性问题 | 小时级 |

---

## 一、核心监控指标

### 1.1 上下文忠实度 (Context Faithfulness)

衡量 Agent 是否利用了对话中已提供的信息。

```python
import hashlib
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FactRecord:
    """记录用户在对话中提供的关键事实"""
    fact_id: str
    content: str
    turn_number: int
    category: str  # e.g., "order_id", "complaint", "preference"
    embedding: Optional[list] = None

class ContextFaithfulnessTracker:
    """
    追踪 Agent 是否忠实使用了对话中收集的信息。
    
    核心思路：维护一个"已知事实库"，每轮检测 Agent 是否
    重新询问已知事实，或是否在响应中正确引用了相关事实。
    """

    def __init__(self, embedding_fn=None):
        self.known_facts: dict[str, FactRecord] = {}
        self.reasked_facts: list[dict] = []
        self.embedding_fn = embedding_fn

    def extract_facts(self, user_message: str, turn_number: int) -> list[FactRecord]:
        """
        从用户消息中提取关键事实。
        生产环境中应使用 NER / LLM 提取，这里用规则兜底。
        """
        facts = []

        # 提取订单号
        import re
        order_ids = re.findall(r'[A-Z]{2,3}\d{6,10}', user_message)
        for oid in order_ids:
            facts.append(FactRecord(
                fact_id=f"order_{oid}",
                content=oid,
                turn_number=turn_number,
                category="order_id"
            ))

        # 提取手机号
        phones = re.findall(r'1[3-9]\d{9}', user_message)
        for phone in phones:
            facts.append(FactRecord(
                fact_id=f"phone_{phone}",
                content=phone,
                turn_number=turn_number,
                category="phone"
            ))

        # 提取日期时间
        dates = re.findall(r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}', user_message)
        for d in dates:
            facts.append(FactRecord(
                fact_id=f"date_{hashlib.md5(d.encode()).hexdigest()[:8]}",
                content=d,
                turn_number=turn_number,
                category="date"
            ))

        # 使用 LLM 提取语义事实（关键诉求、偏好等）
        if self.embedding_fn:
            semantic_facts = self._extract_semantic_facts(user_message, turn_number)
            facts.extend(semantic_facts)

        return facts

    def _extract_semantic_facts(self, message: str, turn: int) -> list[FactRecord]:
        """用 LLM 提取语义级别的事实"""
        prompt = f"""从以下客服对话消息中提取用户表达的关键事实。
        只提取明确陈述的事实，不要推断。

        消息（第{turn}轮）: {message}

        返回 JSON 数组，每个元素包含:
        - fact: 事实内容
        - category: 类别（complaint/preference/requirement/background/other）

        如果没有明确事实，返回空数组 []"""

        # 调用 LLM 提取（伪代码）
        # result = llm_call(prompt)
        # return [FactRecord(...) for item in result]
        return []

    def detect_repetition(self, agent_message: str, turn_number: int) -> list[dict]:
        """
        检测 Agent 是否在重新询问已知事实。
        
        返回: 重复询问的列表，每个包含被重复的事实和置信度。
        """
        repetitions = []

        for fact_id, fact in self.known_facts.items():
            # 跳过最近 2 轮内提供的事实（可能是确认而非重复）
            if turn_number - fact.turn_number <= 2:
                continue

            # 语义相似度检测
            if self.embedding_fn:
                agent_emb = self.embedding_fn(agent_message)
                fact_emb = self.embedding_fn(fact.content)
                similarity = cosine_similarity(agent_emb, fact_emb)
                if similarity > 0.75:
                    repetitions.append({
                        "fact_id": fact_id,
                        "original_turn": fact.turn_number,
                        "current_turn": turn_number,
                        "similarity": similarity,
                        "fact_content": fact.content
                    })
            else:
                # 规则回退：关键词匹配
                if fact.content.lower() in agent_message.lower():
                    # 排除确认性引用（如"您提到的订单号XXX"）
                    confirmation_patterns = [
                        f"您提到的{fact.content}",
                        f"您说的{fact.content}",
                        f"根据您提供的{fact.content}",
                        f"您之前说的{fact.content}",
                    ]
                    if not any(p in agent_message for p in confirmation_patterns):
                        repetitions.append({
                            "fact_id": fact_id,
                            "original_turn": fact.turn_number,
                            "current_turn": turn_number,
                            "fact_content": fact.content
                        })

        return repetitions

    def record_turn(self, user_message: str, agent_message: str, turn_number: int):
        """处理一轮对话，更新状态"""
        # 提取并记录新事实
        new_facts = self.extract_facts(user_message, turn_number)
        for fact in new_facts:
            self.known_facts[fact.fact_id] = fact

        # 检测重复提问
        repetitions = self.detect_repetition(agent_message, turn_number)
        for rep in repetitions:
            self.reasked_facts.append(rep)

    def get_faithfulness_score(self) -> float:
        """
        计算上下文忠实度分数。
        
        1.0 = 完全忠实，0.0 = 严重退化
        
        计算方式：
        - 每次重复询问扣分，扣分幅度随对话轮次递增
          （后期重复说明记忆退化更严重）
        """
        if not self.known_facts:
            return 1.0

        penalty = 0.0
        for rep in self.reasked_facts:
            # 越晚重复，惩罚越重
            turn_ratio = rep["current_turn"] / max(rep["original_turn"], 1)
            penalty += min(turn_ratio * 0.15, 0.3)

        return max(1.0 - penalty, 0.0)
```

### 1.2 信息召回率 (Information Recall Rate)

衡量在需要时，Agent 是否能回忆起对话中的相关信息。

```python
class InformationRecallMonitor:
    """
    监控 Agent 在响应中是否召回了应该使用的信息。
    
    方法：当用户引用之前的信息时，检测 Agent 是否也引用了。
    """

    def __init__(self):
        self.missed_recalls: list[dict] = []
        self.total_recall_opportunities: int = 0

    def check_recall(
        self,
        user_message: str,
        agent_response: str,
        known_facts: dict[str, FactRecord],
        turn_number: int
    ) -> dict:
        """
        检测 Agent 是否在应该引用某信息时没有引用。
        
        例如用户说"我之前提到的那个订单"，Agent 应该找到对应的订单号。
        """
        # 检测用户是否在引用之前的信息
        reference_patterns = [
            "之前说的", "刚才提到", "上次说的", "前面说的",
            "那个订单", "那个问题", "我说过", "已经告诉过你"
        ]

        user_is_referencing = any(p in user_message for p in reference_patterns)

        if not user_is_referencing:
            return {"recall_needed": False}

        self.total_recall_opportunities += 1

        # 检查 Agent 响应是否包含了相关事实
        recalled = False
        for fact_id, fact in known_facts.items():
            if fact.content in agent_response:
                recalled = True
                break

        if not recalled:
            self.missed_recalls.append({
                "turn": turn_number,
                "user_message": user_message,
                "agent_response": agent_response,
                "available_facts": [f.content for f in known_facts.values()]
            })

        return {
            "recall_needed": True,
            "recalled": recalled,
            "score": 1.0 if recalled else 0.0
        }

    def get_recall_rate(self) -> float:
        if self.total_recall_opportunities == 0:
            return 1.0
        return 1.0 - (len(self.missed_recalls) / self.total_recall_opportunities)
```

### 1.3 对话连贯性 (Conversation Coherence)

检测 Agent 是否出现了逻辑跳跃或前后矛盾。

```python
class CoherenceMonitor:
    """
    检测对话连贯性问题：
    - 前后矛盾的回答
    - 逻辑跳跃（突然切换话题）
    - 忘记之前的承诺（如"稍后帮您查"但没有后续）
    """

    def __init__(self, llm_call_fn):
        self.llm_call = llm_call_fn
        self.contradictions: list[dict] = []
        self.dropped_commitments: list[str] = []
        self.pending_commitments: list[dict] = []

    def check_contradiction(
        self,
        conversation_history: list[dict],
        current_response: str
    ) -> Optional[dict]:
        """
        用 LLM 检测当前响应是否与历史对话矛盾。
        """
        # 构建历史摘要
        history_text = "\n".join([
            f"[{msg['role']}][轮次{msg.get('turn', '?')}]: {msg['content']}"
            for msg in conversation_history[-10:]  # 最近 10 轮
        ])

        prompt = f"""分析以下客服对话，判断最新回复是否与之前的信息矛盾。

历史对话:
{history_text}

最新回复:
{current_response}

判断标准:
1. 数字/日期/金额是否前后一致
2. 结论/判断是否前后矛盾
3. 承诺/方案是否前后不一致

返回 JSON:
{{
  "has_contradiction": true/false,
  "description": "矛盾描述（如有）",
  "severity": "high/medium/low",
  "conflicting_turns": [相关轮次]
}}"""

        result = self.llm_call(prompt)

        if result.get("has_contradiction"):
            contradiction = {
                "description": result["description"],
                "severity": result["severity"],
                "turns": result["conflicting_turns"]
            }
            self.contradictions.append(contradiction)
            return contradiction

        return None

    def track_commitments(self, agent_response: str, turn_number: int):
        """
        追踪 Agent 做出的承诺，并检测是否兑现。
        """
        commitment_patterns = [
            (r"稍后.{0,10}(帮您|为您|给您)", "action_promise"),
            (r"(马上|立刻|立即).{0,10}(查|查一下|核实)", "immediate_action"),
            (r"(下一轮|下次|之后).{0,10}(告诉|回复|反馈)", "follow_up_promise"),
            (r"(帮您|为您).{0,5}(转接|升级|转给)", "transfer_promise"),
        ]

        import re
        for pattern, commitment_type in commitment_patterns:
            if re.search(pattern, agent_response):
                self.pending_commitments.append({
                    "type": commitment_type,
                    "turn": turn_number,
                    "context": agent_response[:200],
                    "fulfilled": False
                })

    def check_fulfillment(self, agent_response: str, turn_number: int):
        """检查之前的承诺是否在当前响应中兑现"""
        for commitment in self.pending_commitments:
            if commitment["fulfilled"]:
                continue
            if turn_number - commitment["turn"] > 3:
                self.dropped_commitments.append(commitment["context"])
                commitment["fulfilled"] = True  # 标记为已处理（但未兑现）

    def get_coherence_score(self) -> float:
        score = 1.0
        for c in self.contradictions:
            if c["severity"] == "high":
                score -= 0.3
            elif c["severity"] == "medium":
                score -= 0.15
            else:
                score -= 0.05
        score -= len(self.dropped_commitments) * 0.1
        return max(score, 0.0)
```

### 1.4 对话效率指标

```python
@dataclass
class ConversationEfficiencyMetrics:
    """对话效率相关指标"""
    total_turns: int = 0
    resolution_turns: int = 0  # 达到解决方案的轮次
    repeated_questions: int = 0
    topic_switches: int = 0
    user_frustration_signals: int = 0  # 用户表达不耐烦的次数

    @property
    def efficiency_score(self) -> float:
        """
        效率分数 = 基础分 - 各种惩罚
        
        理想情况：少轮次解决问题，无重复，无用户不满
        """
        if self.total_turns == 0:
            return 1.0

        base = 1.0

        # 轮次惩罚：超过10轮开始扣分
        if self.total_turns > 10:
            base -= min((self.total_turns - 10) * 0.02, 0.3)

        # 重复问题惩罚
        base -= self.repeated_questions * 0.1

        # 用户不满信号惩罚
        frustration_ratio = self.user_frustration_signals / self.total_turns
        base -= frustration_ratio * 0.3

        return max(base, 0.0)

    def detect_user_frustration(self, user_message: str) -> bool:
        """检测用户是否表达了不耐烦"""
        frustration_signals = [
            "你又问", "刚才说了", "你怎么又", "我已经回答过了",
            "你到底有没有在听", "算了", "不想说了", "太麻烦了",
            "你是不是没记住", "换个客服", "投诉", "你是不是傻",
            "again", "already told", "are you listening",
            "I already said", "forget it"
        ]
        return any(s in user_message.lower() for s in frustration_signals)
```

---

## 二、实时检测层 (L1) - 响应拦截

在 Agent 响应返回给用户之前进行质量检测。如果检测到退化，触发补救措施。

```python
class RealTimeGuard:
    """
    L1 实时守卫：在响应返回前检测退化。
    
    设计为可插入到 Agent 调用链中的中间件。
    """

    def __init__(
        self,
        faithfulness_tracker: ContextFaithfulnessTracker,
        recall_monitor: InformationRecallMonitor,
        coherence_monitor: CoherenceMonitor,
        efficiency_metrics: ConversationEfficiencyMetrics,
        config: dict = None
    ):
        self.tracker = faithfulness_tracker
        self.recall = recall_monitor
        self.coherence = coherence_monitor
        self.efficiency = efficiency_metrics
        self.config = config or {
            "min_faithfulness_score": 0.7,
            "min_recall_rate": 0.6,
            "min_coherence_score": 0.7,
            "enable_auto_repair": True,
            "max_repair_attempts": 2,
        }
        self.alerts: list[dict] = []

    def check_and_repair(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        conversation_history: list[dict],
        turn_number: int,
        known_facts: dict
    ) -> dict:
        """
        主入口：检测响应质量，必要时触发修复。
        
        返回:
        {
            "original_response": str,
            "final_response": str,  # 可能被修复
            "was_repaired": bool,
            "checks": {...},  # 各项检查结果
            "alerts": [...]  # 触发的告警
        }
        """
        checks = {}
        alerts = []

        # --- 检查 1: 重复提问 ---
        repetitions = self.tracker.detect_repetition(agent_response, turn_number)
        if repetitions:
            checks["repetition"] = {
                "detected": True,
                "count": len(repetitions),
                "details": repetitions
            }
            alerts.append({
                "type": "repeated_question",
                "severity": "high" if len(repetitions) >= 2 else "medium",
                "conversation_id": conversation_id,
                "turn": turn_number,
                "details": repetitions
            })

        # --- 检查 2: 用户已经表达不满 ---
        if self.efficiency.detect_user_frustration(user_message):
            checks["user_frustration"] = {"detected": True}
            alerts.append({
                "type": "user_frustration",
                "severity": "high",
                "conversation_id": conversation_id,
                "turn": turn_number
            })

        # --- 检查 3: 承诺追踪 ---
        self.coherence.check_fulfillment(agent_response, turn_number)
        self.coherence.track_commitments(agent_response, turn_number)

        # --- 检查 4: 上下文忠实度 ---
        faithfulness_score = self.tracker.get_faithfulness_score()
        checks["faithfulness"] = {"score": faithfulness_score}

        if faithfulness_score < self.config["min_faithfulness_score"]:
            alerts.append({
                "type": "low_faithfulness",
                "severity": "high",
                "conversation_id": conversation_id,
                "turn": turn_number,
                "score": faithfulness_score
            })

        # --- 决定是否需要修复 ---
        needs_repair = (
            (repetitions and self.config["enable_auto_repair"]) or
            (faithfulness_score < self.config["min_faithfulness_score"])
        )

        final_response = agent_response
        was_repaired = False

        if needs_repair:
            repaired = self._attempt_repair(
                agent_response, conversation_history, known_facts,
                repetitions, turn_number
            )
            if repaired:
                final_response = repaired
                was_repaired = True

        # 更新效率指标
        self.efficiency.total_turns = turn_number
        if repetitions:
            self.efficiency.repeated_questions += len(repetitions)

        self.alerts.extend(alerts)

        return {
            "original_response": agent_response,
            "final_response": final_response,
            "was_repaired": was_repaired,
            "checks": checks,
            "alerts": alerts
        }

    def _attempt_repair(
        self,
        response: str,
        history: list[dict],
        known_facts: dict,
        repetitions: list[dict],
        turn: int
    ) -> Optional[str]:
        """
        尝试修复退化的响应。
        
        策略：
        1. 注入上下文提示，提醒 Agent 已知信息
        2. 移除重复的问题
        3. 重新生成响应
        """
        # 构建修复提示
        facts_summary = "\n".join([
            f"- {f.category}: {f.content}（第{f.turn_number}轮提供）"
            for f in known_facts.values()
        ])

        repeated_info = "\n".join([
            f"- {r['fact_content']}（第{r['original_turn']}轮已提供）"
            for r in repetitions
        ])

        repair_prompt = f"""你之前的回复存在问题，需要修正。

已知的用户信息（绝对不要重新询问这些信息）:
{facts_summary}

你重复询问了以下已知信息:
{repeated_info}

你的原始回复:
{response}

要求：
1. 移除对已知信息的重复询问
2. 保持回复的其他有价值内容
3. 如果需要引用已知信息，直接使用而不是重新询问
4. 回复要自然流畅

请给出修正后的回复:"""

        # 调用 LLM 修复（伪代码）
        # repaired = llm_call(repair_prompt)
        # return repaired
        return None  # 占位，实际实现需要接入 LLM
```

---

## 三、近实时监控层 (L2) - 会话结束评估

每次会话结束后立即评估整体质量。

```python
from datetime import datetime
from enum import Enum

class SessionQuality(Enum):
    EXCELLENT = "excellent"    # 90-100
    GOOD = "good"              # 70-89
    DEGRADED = "degraded"      # 50-69
    POOR = "poor"              # 30-49
    CRITICAL = "critical"      # 0-29

@dataclass
class SessionReport:
    """单次会话的质量报告"""
    session_id: str
    timestamp: str
    total_turns: int
    faithfulness_score: float
    recall_rate: float
    coherence_score: float
    efficiency_score: float
    overall_score: float
    quality_level: SessionQuality
    repeated_questions: int
    user_frustration_count: int
    dropped_commitments: int
    contradictions: list
    alerts: list
    root_causes: list[str]

class SessionEvaluator:
    """
    L2 会话评估器：会话结束后生成完整质量报告。
    """

    def __init__(self, llm_call_fn=None):
        self.llm_call = llm_call_fn

    def evaluate_session(
        self,
        session_id: str,
        conversation_history: list[dict],
        faithfulness_tracker: ContextFaithfulnessTracker,
        recall_monitor: InformationRecallMonitor,
        coherence_monitor: CoherenceMonitor,
        efficiency_metrics: ConversationEfficiencyMetrics
    ) -> SessionReport:
        """生成会话质量报告"""

        # 计算各项分数
        faithfulness = faithfulness_tracker.get_faithfulness_score()
        recall = recall_monitor.get_recall_rate()
        coherence = coherence_monitor.get_coherence_score()
        efficiency = efficiency_metrics.efficiency_score

        # 加权计算总分
        weights = {
            "faithfulness": 0.30,
            "recall": 0.25,
            "coherence": 0.25,
            "efficiency": 0.20
        }

        overall = (
            faithfulness * weights["faithfulness"] +
            recall * weights["recall"] +
            coherence * weights["coherence"] +
            efficiency * weights["efficiency"]
        )

        # 确定质量等级
        if overall >= 0.9:
            quality = SessionQuality.EXCELLENT
        elif overall >= 0.7:
            quality = SessionQuality.GOOD
        elif overall >= 0.5:
            quality = SessionQuality.DEGRADED
        elif overall >= 0.3:
            quality = SessionQuality.POOR
        else:
            quality = SessionQuality.CRITICAL

        # 诊断根因
        root_causes = self._diagnose_root_causes(
            faithfulness, recall, coherence, efficiency,
            faithfulness_tracker, efficiency_metrics
        )

        report = SessionReport(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            total_turns=efficiency_metrics.total_turns,
            faithfulness_score=round(faithfulness, 3),
            recall_rate=round(recall, 3),
            coherence_score=round(coherence, 3),
            efficiency_score=round(efficiency, 3),
            overall_score=round(overall, 3),
            quality_level=quality,
            repeated_questions=efficiency_metrics.repeated_questions,
            user_frustration_count=efficiency_metrics.user_frustration_signals,
            dropped_commitments=len(coherence_monitor.dropped_commitments),
            contradictions=coherence_monitor.contradictions,
            alerts=[],
            root_causes=root_causes
        )

        return report

    def _diagnose_root_causes(
        self, faithfulness, recall, coherence, efficiency,
        tracker, metrics
    ) -> list[str]:
        """自动诊断退化的根因"""
        causes = []

        if faithfulness < 0.6:
            causes.append("CONTEXT_OVERFLOW: 上下文可能超出有效处理长度，关键信息被淹没")

        if recall < 0.5:
            causes.append("RECALL_FAILURE: Agent 无法在需要时召回相关信息，可能是检索策略问题")

        if tracker.reasked_facts and len(tracker.reasked_facts) > 3:
            causes.append("MEMORY_DECAY: Agent 对话记忆随轮次衰减明显")

        if metrics.repeated_questions > 2:
            causes.append("STATE_LOSS: 对话状态管理可能有缺陷，未正确维护已收集信息")

        if metrics.user_frustration_signals > 1:
            causes.append("UX_DEGRADATION: 用户体验严重退化，需要立即关注")

        if efficiency < 0.5 and metrics.total_turns > 15:
            causes.append("EFFICIENCY_LOSS: 长对话中效率下降，考虑引入摘要或分段策略")

        if not causes:
            causes.append("NO_MAJOR_ISSUES: 会话质量在可接受范围内")

        return causes
```

---

## 四、离线分析层 (L3) - 批量分析与趋势

```python
class OfflineAnalyzer:
    """
    L3 离线分析：批量分析历史会话，发现系统性问题和趋势。
    """

    def __init__(self, storage_backend=None):
        self.storage = storage_backend  # 数据库存储
        self.sessions: list[SessionReport] = []

    def add_session(self, report: SessionReport):
        self.sessions.append(report)

    def analyze_degradation_patterns(self) -> dict:
        """
        分析退化模式：
        1. 退化是否随轮次增加而加重
        2. 哪些类型的会话更容易退化
        3. 退化的常见根因
        """
        if not self.sessions:
            return {"error": "no_data"}

        # 1. 轮次 vs 质量分析
        turn_quality_correlation = {}
        for s in self.sessions:
            bucket = (s.total_turns // 5) * 5  # 5轮一个桶
            if bucket not in turn_quality_correlation:
                turn_quality_correlation[bucket] = []
            turn_quality_correlation[bucket].append(s.overall_score)

        turn_quality_trend = {
            bucket: {
                "avg_score": round(sum(scores) / len(scores), 3),
                "min_score": round(min(scores), 3),
                "sample_count": len(scores)
            }
            for bucket, scores in sorted(turn_quality_correlation.items())
        }

        # 2. 退化会话的根因分布
        root_cause_distribution = {}
        degraded_sessions = [
            s for s in self.sessions
            if s.quality_level in (SessionQuality.DEGRADED, SessionQuality.POOR, SessionQuality.CRITICAL)
        ]
        for s in degraded_sessions:
            for cause in s.root_causes:
                cause_code = cause.split(":")[0]
                root_cause_distribution[cause_code] = root_cause_distribution.get(cause_code, 0) + 1

        # 3. 重复问题的触发模式
        repetition_by_turn = {}
        for s in self.sessions:
            for r in range(1, s.total_turns + 1):
                # 统计每一轮出现重复问题的频率
                pass  # 需要更细粒度的数据

        # 4. 整体健康度
        avg_score = sum(s.overall_score for s in self.sessions) / len(self.sessions)
        degraded_ratio = len(degraded_sessions) / len(self.sessions)

        return {
            "summary": {
                "total_sessions": len(self.sessions),
                "avg_quality_score": round(avg_score, 3),
                "degraded_session_ratio": round(degraded_ratio, 3),
                "critical_sessions": sum(1 for s in self.sessions if s.quality_level == SessionQuality.CRITICAL)
            },
            "turn_quality_trend": turn_quality_trend,
            "root_cause_distribution": root_cause_distribution,
            "recommendations": self._generate_recommendations(
                turn_quality_trend, root_cause_distribution, degraded_ratio
            )
        }

    def _generate_recommendations(
        self, trend: dict, causes: dict, degraded_ratio: float
    ) -> list[str]:
        """基于分析结果生成改进建议"""
        recs = []

        # 检查是否有轮次退化趋势
        if len(trend) >= 2:
            buckets = sorted(trend.keys())
            first_avg = trend[buckets[0]]["avg_score"]
            last_avg = trend[buckets[-1]]["avg_score"]
            if first_avg - last_avg > 0.2:
                recs.append(
                    f"轮次退化明显：{buckets[0]}轮时平均分{first_avg}，"
                    f"{buckets[-1]}轮时降至{last_avg}。"
                    f"建议在第{buckets[1]}轮后启用对话摘要。"
                )

        # 检查根因
        if causes.get("CONTEXT_OVERFLOW", 0) > len(self.sessions) * 0.1:
            recs.append(
                "上下文溢出问题频发。建议：1) 增加对话摘要频率 "
                "2) 实现基于重要性的上下文裁剪 3) 使用 RAG 检索历史信息"
            )

        if causes.get("MEMORY_DECAY", 0) > len(self.sessions) * 0.1:
            recs.append(
                "记忆衰减问题明显。建议：1) 维护结构化的会话状态 "
                "2) 在每轮注入关键事实摘要 3) 使用外部记忆存储"
            )

        if causes.get("STATE_LOSS", 0) > len(self.sessions) * 0.1:
            recs.append(
                "对话状态丢失。建议：1) 实现显式的槽位填充机制 "
                "2) 在 prompt 中维护已收集信息的清单 "
                "3) 禁止 Agent 询问清单中已有的信息"
            )

        if degraded_ratio > 0.3:
            recs.append(
                f"退化会话比例 {degraded_ratio:.1%} 过高。"
                f"建议从根本上优化长对话处理策略，"
                f"考虑采用分段对话架构。"
            )

        if not recs:
            recs.append("当前会话质量整体健康，继续保持监控。")

        return recs
```

---

## 五、告警与仪表盘

### 5.1 告警规则

```python
class AlertManager:
    """
    告警管理器：根据规则触发不同级别的告警。
    """

    def __init(self, notification_fn=None):
        self.notification_fn = notification_fn
        self.alert_rules = [
            # 实时告警（L1）
            {
                "name": "repeated_question_realtime",
                "condition": lambda checks: checks.get("repetition", {}).get("count", 0) >= 2,
                "severity": "high",
                "message": "Agent 在单轮中重复询问 2+ 个已知信息"
            },
            {
                "name": "user_frustration",
                "condition": lambda checks: checks.get("user_frustration", {}).get("detected"),
                "severity": "high",
                "message": "用户表达了对 Agent 记忆的不满"
            },
            # 会话级告警（L2）
            {
                "name": "session_critical",
                "condition": lambda report: report.quality_level == SessionQuality.CRITICAL,
                "severity": "critical",
                "message": "会话质量降至危急水平，需要人工介入"
            },
            {
                "name": "session_degraded",
                "condition": lambda report: report.quality_level == SessionQuality.DEGRADED,
                "severity": "medium",
                "message": "会话质量退化，建议关注"
            },
            # 批量告警（L3）
            {
                "name": "degradation_spike",
                "condition": lambda analysis: analysis.get("summary", {}).get("degraded_session_ratio", 0) > 0.3,
                "severity": "critical",
                "message": "退化会话比例超过 30%，系统性问题"
            },
        ]

    def evaluate(self, context: dict):
        """评估所有规则并触发告警"""
        triggered = []
        for rule in self.alert_rules:
            try:
                if rule["condition"](context):
                    alert = {
                        "rule": rule["name"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "timestamp": datetime.now().isoformat(),
                        "context": context
                    }
                    triggered.append(alert)
                    if self.notification_fn:
                        self.notification_fn(alert)
            except Exception as e:
                # 规则执行失败不应阻断流程
                pass
        return triggered
```

### 5.2 仪表盘指标

建议在 Grafana / Datadog 等工具中配置以下仪表盘：

```
┌─────────────────────────────────────────────────────────────────┐
│                    客服 Agent 长对话健康度仪表盘                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ 实时指标 ─────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  当前活跃会话: 142    平均轮次: 8.3    退化会话: 12 (8.5%) │  │
│  │                                                            │  │
│  │  过去1小时:                                                │  │
│  │  平均忠实度: 0.87 ▲    召回率: 0.91 ▲    连贯性: 0.89 ▼   │  │
│  │                                                            │  │
│  │  [████████████████████░░] 87% 健康会话比例                 │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─ 轮次 vs 质量趋势 ────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  1.0 ┤                                                     │  │
│  │      │ ●                                                   │  │
│  │  0.9 ┤   ●                                                 │  │
│  │      │     ●                                               │  │
│  │  0.8 ┤       ●                                             │  │
│  │      │         ●                                           │  │
│  │  0.7 ┤           ●                                         │  │
│  │      │             ●                                       │  │
│  │  0.6 ┤               ●                                     │  │
│  │      │                 ●                                   │  │
│  │  0.5 ┤                   ●  ← 需要干预的阈值               │  │
│  │      └──┬──┬──┬──┬──┬──┬──┬──┬──┬──                       │  │
│  │         5  10 15 20 25 30 35 40 45  对话轮次               │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─ 退化根因分布 ────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  CONTEXT_OVERFLOW  ████████████████████  38%               │  │
│  │  MEMORY_DECAY      ████████████████      31%               │  │
│  │  STATE_LOSS        ██████████            19%               │  │
│  │  RECALL_FAILURE    ████                   8%               │  │
│  │  UX_DEGRADATION    ██                     4%               │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─ 告警历史 ────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  14:23  [HIGH]     会话 abc-123: 用户表达不满               │  │
│  │  14:18  [CRITICAL] 会话 def-456: 质量降至危急               │  │
│  │  14:15  [MEDIUM]   会话 ghi-789: 检测到重复提问             │  │
│  │  14:10  [HIGH]     会话 jkl-012: 忠实度低于阈值             │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、预防策略

监控能发现问题，但更重要的是预防。以下是针对长对话退化的预防措施：

### 6.1 结构化对话状态管理

```python
class StructuredDialogState:
    """
    维护结构化的对话状态，而不是依赖 LLM 自己记住。
    
    核心思想：关键信息从对话中提取出来，存入结构化字段，
    每轮 prompt 中注入当前状态摘要。
    """

    def __init__(self):
        self.slot_schema = {
            "user_intent": None,           # 用户意图
            "order_id": None,              # 订单号
            "issue_type": None,            # 问题类型
            "issue_description": None,     # 问题描述
            "urgency": None,               # 紧急程度
            "contact_preference": None,    # 联系偏好
            "previous_solutions": [],      # 已尝试的解决方案
            "user_sentiment": "neutral",   # 用户情绪
            "collected_info": {},          # 其他收集到的信息
            "pending_actions": [],         # 待执行的动作
            "resolved_items": [],          # 已解决的事项
        }
        self.turn_history = []
        self.fact_timeline = []  # 事实的时序记录

    def update(self, user_message: str, agent_response: str, turn: int):
        """每轮对话后更新状态"""
        self.turn_history.append({
            "turn": turn,
            "user": user_message,
            "agent": agent_response
        })

        # 更新槽位（实际实现中用 LLM 或规则提取）
        # extracted = extract_slots(user_message)
        # self.slot_schema.update(extracted)

    def get_context_prompt(self) -> str:
        """
        生成注入到 prompt 中的状态摘要。
        
        这是防止退化的核心机制：每轮都明确告诉 Agent
        当前已知的所有信息，避免它"忘记"。
        """
        filled_slots = {
            k: v for k, v in self.slot_schema.items()
            if v is not None and v != [] and v != {}
        }

        if not filled_slots:
            return ""

        lines = ["[系统维护的对话状态 - 请勿重复询问以下已有信息]"]
        for key, value in filled_slots.items():
            display_name = key.replace("_", " ").title()
            if isinstance(value, list):
                lines.append(f"- {display_name}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"- {display_name}: {value}")

        # 添加最近的待办事项
        if self.slot_schema["pending_actions"]:
            lines.append("\n[待执行动作]")
            for action in self.slot_schema["pending_actions"]:
                lines.append(f"- {action}")

        return "\n".join(lines)
```

### 6.2 智能上下文窗口管理

```python
class ContextWindowManager:
    """
    管理发送给 LLM 的上下文，确保关键信息不被截断。
    
    策略：固定保留"状态摘要 + 最近N轮"，中间的对话用摘要替代。
    """

    def __init__(
        self,
        max_context_turns: int = 10,
        summary_interval: int = 8,
        llm_call_fn = None
    ):
        self.max_context_turns = max_context_turns
        self.summary_interval = summary_interval
        self.llm_call = llm_call_fn
        self.summaries: list[dict] = []  # {turn_range, summary}
        self.full_history: list[dict] = []

    def build_context(
        self,
        dialog_state: StructuredDialogState,
        current_turn: int
    ) -> list[dict]:
        """
        构建发送给 LLM 的上下文消息列表。
        
        结构：
        1. 系统提示 + 状态摘要
        2. 早期对话的摘要（如果有）
        3. 最近 N 轮的完整对话
        4. 当前用户消息
        """
        messages = []

        # 1. 系统提示 + 结构化状态
        state_prompt = dialog_state.get_context_prompt()
        system_content = f"""你是一个专业的客服助手。请基于对话历史为用户提供帮助。

{state_prompt}

重要规则：
- 不要询问上述状态中已有答案的问题
- 引用已知信息时使用确认性语气（如"您之前提到的订单号XXX"）
- 如果信息不完整，只询问缺失的部分"""

        messages.append({"role": "system", "content": system_content})

        # 2. 早期对话摘要
        if self.summaries:
            summary_text = "\n".join([
                f"[对话摘要 {s['turn_range']}]: {s['summary']}"
                for s in self.summaries
            ])
            messages.append({
                "role": "system",
                "content": f"以下是更早对话的摘要:\n{summary_text}"
            })

        # 3. 最近 N 轮完整对话
        recent_start = max(0, len(self.full_history) - self.max_context_turns * 2)
        recent = self.full_history[recent_start:]
        messages.extend(recent)

        return messages

    def should_summarize(self, current_turn: int) -> bool:
        """判断是否需要生成新的摘要"""
        return (
            current_turn > 0 and
            current_turn % self.summary_interval == 0 and
            len(self.full_history) > self.max_context_turns * 2
        )

    def generate_summary(self) -> str:
        """生成对话摘要"""
        if not self.llm_call:
            return ""

        # 取需要被摘要的对话段
        summary_end = len(self.full_history) - self.max_context_turns * 2
        to_summarize = self.full_history[:summary_end]

        conversation_text = "\n".join([
            f"[{msg['role']}]: {msg['content']}"
            for msg in to_summarize
        ])

        prompt = f"""请为以下客服对话生成简洁摘要，保留所有关键信息（订单号、问题描述、承诺、解决方案等）。

对话:
{conversation_text}

要求：
- 保留所有具体的数字、日期、订单号
- 保留用户的主要诉求和已尝试的方案
- 保留客服做出的承诺
- 不超过 200 字"""

        summary = self.llm_call(prompt)
        self.summaries.append({
            "turn_range": f"1-{summary_end // 2}",
            "summary": summary
        })

        return summary
```

### 6.3 反重复注入机制

```python
class AntiRepetitionInjector:
    """
    在 prompt 中显式注入"禁止重复询问"的指令。
    这是一个简单但有效的预防措施。
    """

    def __init__(self):
        self.collected_slots: dict[str, str] = {}

    def build_negative_examples(self, known_facts: dict) -> str:
        """
        构建明确的"不要问"指令。
        
        比告诉 Agent "要记住信息"更有效的是
        告诉它"绝对不要问以下问题"。
        """
        if not known_facts:
            return ""

        dont_ask = ["[以下是用户已提供的信息，绝对不要重新询问]"]
        for fact_id, fact in known_facts.items():
            dont_ask.append(f"- {fact.category}: {fact.content}（第{fact.turn_number}轮已提供）")

        dont_ask.append("")
        dont_ask.append("如果需要引用上述信息，请直接使用并确认，例如：")
        dont_ask.append('"您之前提到的订单号是 XXX，我来帮您查看..."')
        dont_ask.append("")
        dont_ask.append("绝对不要说：")
        dont_ask.append('"请问您的订单号是多少？"  ← 这是禁止的，因为已经知道了')

        return "\n".join(dont_ask)
```

---

## 七、完整集成示例

```python
class MonitoredCustomerServiceAgent:
    """
    完整的带监控的客服 Agent。
    
    展示如何将监控方案集成到实际的 Agent 中。
    """

    def __init__(self, llm_call_fn):
        self.llm_call = llm_call_fn

        # 监控组件
        self.faithfulness_tracker = ContextFaithfulnessTracker()
        self.recall_monitor = InformationRecallMonitor()
        self.coherence_monitor = CoherenceMonitor(llm_call_fn)
        self.efficiency_metrics = ConversationEfficiencyMetrics()

        # 预防组件
        self.dialog_state = StructuredDialogState()
        self.context_manager = ContextWindowManager(llm_call_fn=llm_call_fn)
        self.anti_repetition = AntiRepetitionInjector()

        # 实时守卫
        self.guard = RealTimeGuard(
            self.faithfulness_tracker,
            self.recall_monitor,
            self.coherence_monitor,
            self.efficiency_metrics
        )

        # 会话评估
        self.evaluator = SessionEvaluator(llm_call_fn)

    def handle_message(
        self,
        session_id: str,
        user_message: str,
        turn_number: int
    ) -> dict:
        """处理一轮对话"""

        # 1. 更新对话状态
        self.dialog_state.update(user_message, "", turn_number)

        # 2. 检查是否需要生成摘要
        if self.context_manager.should_summarize(turn_number):
            self.context_manager.generate_summary()

        # 3. 构建上下文（含状态摘要 + 反重复注入）
        messages = self.context_manager.build_context(
            self.dialog_state, turn_number
        )

        # 注入反重复指令
        anti_reprompt = self.anti_repetition.build_negative_examples(
            self.faithfulness_tracker.known_facts
        )
        if anti_reprompt:
            messages.insert(1, {
                "role": "system",
                "content": anti_reprompt
            })

        # 4. 调用 LLM 生成响应
        agent_response = self.llm_call(messages)

        # 5. L1 实时检测
        guard_result = self.guard.check_and_repair(
            session_id=session_id,
            user_message=user_message,
            agent_response=agent_response,
            conversation_history=self.dialog_state.turn_history,
            turn_number=turn_number,
            known_facts=self.faithfulness_tracker.known_facts
        )

        final_response = guard_result["final_response"]

        # 6. 更新监控状态
        self.faithfulness_tracker.record_turn(
            user_message, final_response, turn_number
        )
        self.recall_monitor.check_recall(
            user_message, final_response,
            self.faithfulness_tracker.known_facts, turn_number
        )
        if self.efficiency_metrics.detect_user_frustration(user_message):
            self.efficiency_metrics.user_frustration_signals += 1

        # 7. 更新对话状态（含 Agent 回复）
        self.dialog_state.update(user_message, final_response, turn_number)
        self.context_manager.full_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": final_response}
        ])

        return {
            "response": final_response,
            "was_repaired": guard_result["was_repaired"],
            "quality_checks": guard_result["checks"],
            "alerts": guard_result["alerts"]
        }

    def end_session(self, session_id: str) -> SessionReport:
        """会话结束时生成质量报告"""
        report = self.evaluator.evaluate_session(
            session_id=session_id,
            conversation_history=self.dialog_state.turn_history,
            faithfulness_tracker=self.faithfulness_tracker,
            recall_monitor=self.recall_monitor,
            coherence_monitor=self.coherence_monitor,
            efficiency_metrics=self.efficiency_metrics
        )

        return report
```

---

## 八、部署建议

### 8.1 渐进式上线

```
阶段 1（第1周）: 只开启监控，不干预
  - 收集基线数据
  - 验证指标准确性
  - 调整阈值

阶段 2（第2周）: 开启 L1 实时检测（只记录，不修复）
  - 验证检测的准确率（precision/recall）
  - 减少误报

阶段 3（第3周）: 开启自动修复
  - 对低置信度的修复保持人工审核
  - 监控修复成功率

阶段 4（持续）: 完整监控 + 自动修复 + 离线分析
  - 定期回顾离线分析报告
  - 持续优化阈值和策略
```

### 8.2 性能考量

| 组件 | 预计延迟 | 优化建议 |
|------|----------|----------|
| 事实提取 | 50-100ms | 规则提取先行，LLM 异步补充 |
| 重复检测 | 10-50ms | 使用向量索引加速相似度计算 |
| 连贯性检查 | 200-500ms | 仅在可疑时触发，非常规检查 |
| 上下文构建 | 5-20ms | 缓存摘要结果 |
| 自动修复 | 500-1000ms | 仅在检测到问题时触发 |

### 8.3 成本控制

- L1 实时检测中的 LLM 调用：使用小模型（如 Claude Haiku）做初步检测
- L3 离线分析：在低峰期批量处理
- 向量化缓存：避免重复计算相同内容的 embedding
- 采样策略：对健康会话降低检测频率，对已退化会话提高检测频率

---

## 九、指标总结

| 指标 | 计算方式 | 健康阈值 | 告警阈值 |
|------|----------|----------|----------|
| 上下文忠实度 | 1 - (重复询问惩罚) | >= 0.7 | < 0.5 |
| 信息召回率 | 成功召回次数 / 应召回次数 | >= 0.8 | < 0.6 |
| 对话连贯性 | 1 - (矛盾惩罚 + 承诺遗漏惩罚) | >= 0.7 | < 0.5 |
| 对话效率 | 基于轮次/重复/不满的综合分 | >= 0.7 | < 0.5 |
| 用户挫败感 | 检测到不满信号的次数 | 0 | >= 2 |
| 退化会话比例 | 退化会话数 / 总会话数 | < 10% | >= 30% |

---

## 十、快速开始

如果需要最快落地，优先实现以下三个组件：

1. **StructuralDialogState** + **反重复注入**：成本最低，效果最直接
2. **重复提问检测**（规则版本）：不需要 LLM，纯规则即可拦截大部分问题
3. **会话结束评估**：建立基线数据，为后续优化提供依据

这三个组件可以在 1-2 天内实现并上线，覆盖 80% 的常见退化场景。
