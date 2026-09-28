import re

file_path = r'c:\up_prices\frontend\src\components\jobs\ValidationIssueList.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = content.replace(
    'import { ValidationIssueResponse } from "@/types";',
    'import { ValidationIssueResponse, AIAnomalyExplanation } from "@/types";\nimport { explainIssueWithAi } from "@/lib/api";'
)

# 2. State variables
content = content.replace(
    'const [isAiExplaining, setIsAiExplaining] = useState(false);',
    'const [isAiExplaining, setIsAiExplaining] = useState(false);\n  const [aiExplanation, setAiExplanation] = useState<AIAnomalyExplanation | null>(null);'
)

# 3. handleExplainWithAi function
content = re.sub(
    r'  const handleExplainWithAi = \(issue: ValidationIssueResponse\) => \{.*?\};',
    '''  const handleExplainWithAi = async (issue: ValidationIssueResponse) => {
    setSelectedIssue(issue);
    setIsAiExplaining(true);
    setAiExplanation(null);
    try {
      const result = await explainIssueWithAi(issue.job_id, {
        issue_code: issue.code,
        issue_message: issue.message,
        severity: issue.severity,
      });
      setAiExplanation(result.data);
    } catch (error) {
      console.error('Erro ao obter explicação da IA', error);
      setAiExplanation({
        title: 'Erro de Comunicação',
        plain_explanation: 'Não foi possível obter a explicação da IA no momento.',
        likely_cause: 'Serviço indisponível ou erro de rede.',
        suggested_action: 'Tente novamente mais tarde.',
        is_blocker: false,
      });
    } finally {
      setIsAiExplaining(false);
    }
  };''',
    content,
    flags=re.DOTALL
)

# 4. Rendered dialog content
content = re.sub(
    r'<div className="space-y-2.5 text-ink/90 leading-relaxed bg-brand-subtle/30 p-3 rounded border border-brand/20">.*?</div>',
    '''<div className="space-y-2.5 text-ink/90 leading-relaxed bg-brand-subtle/30 p-3 rounded border border-brand/20">
                  <p>
                    <strong>Causa Raiz:</strong> {aiExplanation?.likely_cause}
                  </p>
                  <p>
                    <strong>Explicação:</strong> {aiExplanation?.plain_explanation}
                  </p>
                  <p>
                    <strong>Ação Recomendada:</strong> {aiExplanation?.suggested_action}
                  </p>
                  {aiExplanation?.is_blocker && (
                    <p className="text-error font-bold">Este problema bloqueia o processamento e requer intervenção.</p>
                  )}
                  <p className="text-[11px] text-slateSecondary border-t border-border pt-2 italic">
                    Guardrail: De acordo com a governança CCM, anomalias de preço requerem revisão manual ou retificação da folha de cálculo pela equipa Comercial antes da aprovação do Operador.
                  </p>
                </div>''',
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
