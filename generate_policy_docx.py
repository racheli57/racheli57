#!/usr/bin/env python3
"""批量生成深圳知识产权海外维权能力提升资助项目推广文档。

内置 build_ip_rights_article()，可一次生成 10 篇不同风格宣传稿，
并同步输出 docx 文件与 generated_documents.md 汇总清单。

文案会结合可配置的公司业务资料（行业、产品、海外市场、知识产权资产和维权场景）生成；默认资料为示例化业务信息，不包含真实客户名单、项目编号、销售数据等敏感信息。
"""
from __future__ import annotations

import argparse
import html
import re
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List

POLICY_NAME = "2026年度知识产权海外维权能力提升资助项目申报指南"
DEFAULT_OUTPUT_DIR = Path("generated_policy_docs")
DEFAULT_SUMMARY = Path("generated_documents.md")

# 新增业务分支：深圳知识产权海外维权能力提升资助。
# 保持原有批量推广文章生成入口不变，仅将本次政策作为一个业务分支挂载。
IP_RIGHTS_BRANCH = "ip_rights_overseas_support_2026"

POLICY_RULES = {
    "basis": "《深圳市市场监督管理局知识产权领域专项资金操作规程》（深市监规〔2024〕5号）",
    "support": "支持企业“走出去”，提升主动开展海外维权、积极应对海外纠纷的意识。",
    "cap_per_project": "每个项目按照实际支出成本资助，资助上限不超过200万元。",
    "deductions": "项目获得的知识产权侵权相关保险赔付款、支付的和解费用应予以扣除。",
    "annual_limit": "同一申请人每年度资助不超过1项；本项目每年资助总额不超过3000万元。",
    "exclusion_337": "不含美国“337”调查案件。",
}

APPLICATION_CONDITIONS = [
    "依法登记注册的企业，在深圳市从事生产经营活动，在深圳市拥有稳定办公场所，积极实施深圳市知识产权保护和运用“十四五”规划。",
    "建立较完善的知识产权保护制度，包含但不限于人员管理、合规管理、侵权预警或风险防控等。",
    "维权项目有判决、仲裁裁决或和解协议，且相关文书没有载明申请人构成侵权。",
    "项目完成时间为上三年度1月1日起至申请截止日止，完成时间以判决、裁决或和解协议生效之日为准。",
    "项目体现企业知识产权保护能力和海外维权水平提升，对深圳相关产业具有借鉴作用，或对知识产权保护政策制定具有参考意义，或具有社会意义和影响。",
    "同意将项目有关信息（商业秘密等除外）、研究成果、维权经验等向社会公开及供他人无偿使用。",
]

INELIGIBLE_CASES = [
    "不符合相关法律、法规、规章、专项资金管理办法、专项资金操作规程有关要求。",
    "经查询深圳市信用网，依法依规被纳入严重失信主体名单。",
    "所申请项目已经获得市级同类资助或者奖励。",
    "申请人主体已经消亡，或者进入破产清算程序。",
]

STYLES = [
    ("重磅政策助力深圳企业海外维权申报", "政策解读型", "重磅利好正在释放"),
    ("最高两百万元支持企业出海护权行动", "标题新闻型", "出海竞争，知识产权先行"),
    ("海外纠纷不用慌深圳资助来护航指南", "场景痛点型", "面对跨境侵权，企业不必孤军奋战"),
    ("深圳企业海外维权申报指南重点速读", "清单速读型", "把复杂政策读成一张行动清单"),
    ("出海品牌如何稳稳拿好维权补贴指南", "顾问建议型", "把维权经验沉淀为企业能力"),
    ("深圳知识产权海外护航计划正式来了", "品牌传播型", "让深圳创新在全球市场更有底气"),
    ("从纠纷到补贴企业应当这样申报指南", "流程指导型", "已经完成海外维权项目的企业请重点关注"),
    ("深圳出海企业维权成本可获专项支持", "成本减负型", "高额维权支出有机会获得专项资金支持"),
    ("海外知识产权攻防深圳给出政策答案", "战略倡议型", "从被动应诉走向主动保护"),
    ("用政策资金放大企业海外维权价值", "成果转化型", "一次维权，不止解决一个案件"),
]


@dataclass(frozen=True)
class CompanyProfile:
    """用于把政策推广文案与公司业务资料结合。"""

    name: str
    industry: str
    products: str
    overseas_markets: str
    ip_assets: str
    rights_scenario: str
    compliance_basis: str


DEFAULT_COMPANY_PROFILE = CompanyProfile(
    name="深圳出海创新企业",
    industry="智能硬件、消费电子与跨境数字服务",
    products="自主品牌终端设备、配套软件平台、外观设计产品和海外电商运营服务",
    overseas_markets="东南亚、欧洲、中东和拉美等重点市场",
    ip_assets="境内外商标、发明及实用新型专利、外观设计专利、软件著作权和品牌素材版权",
    rights_scenario="海外平台仿冒链接、商标抢注、专利侵权警告、经销渠道混淆和跨境纠纷应对",
    compliance_basis="已建立知识产权台账、人员分工、合同合规审查、侵权预警和证据留存机制",
)


@dataclass(frozen=True)
class Article:
    index: int
    title: str
    style: str
    body: str


def _paragraphs(style_name: str, hook: str, index: int, company: CompanyProfile) -> List[str]:
    business_intro = (
        f"以{company.name}为例，其业务覆盖{company.industry}，主要产品和服务包括{company.products}，"
        f"海外布局聚焦{company.overseas_markets}，核心知识产权资产涵盖{company.ip_assets}。"
    )
    business_risk = (
        f"企业在出海过程中常见的维权场景包括{company.rights_scenario}，"
        f"内部管理基础则体现为{company.compliance_basis}。"
    )
    angles = [
        "深圳企业加速进入全球市场，专利、商标、著作权和商业秘密的保护半径也随之延伸。" + business_intro + "海外市场一旦发生侵权、抢注、诉讼或仲裁，企业往往需要投入律师费、调查费、公证认证费、翻译费和差旅协调成本。2026年度知识产权海外维权能力提升资助项目，正是面向这些真实出海场景推出的专项支持。",
        "本项目的核心信号很明确：鼓励企业敢维权、会维权、善复盘。政策依据为《深圳市市场监督管理局知识产权领域专项资金操作规程》（深市监规〔2024〕5号），支持企业“走出去”，提升主动开展海外维权、积极应对海外纠纷的意识。对符合条件的海外知识产权维权项目，按实际支出成本给予资助，每个项目资助上限不超过200万元。",
        "需要特别注意的是，美国“337”调查案件不纳入本项目范围。项目获得的知识产权侵权相关保险赔付款、已经支付或承担的和解费用，应在核算时予以扣除。同一申请人每年度资助不超过1项，本项目年度资助总额不超过3000万元，因此企业既要重视材料质量，也要尽早梳理项目完整性。",
        "哪些企业适合重点关注？首先，申请人应为依法登记注册的企业，在深圳市从事生产经营活动，并在深圳拥有稳定办公场所；其次，企业应建立较完善的知识产权保护制度，包括人员管理、合规管理、侵权预警或风险防控等机制。" + business_risk + "这意味着申报不只是提交一场纠纷的材料，更是在展示企业长期知识产权治理能力。",
        "项目本身也有明确门槛：维权项目应当已经形成判决、仲裁裁决或和解协议，且相关文书没有载明申请人构成侵权；项目完成时间为上三年度1月1日起至申请截止日止，完成时间以判决、裁决或和解协议生效之日为准。企业在准备材料时，应优先核对生效日期、费用发生期间、付款凭证和项目对应关系。",
        "从传播价值看，政策鼓励具有示范意义的项目。项目应体现企业知识产权保护能力和海外维权水平的提升，对深圳相关产业具有借鉴作用，对深圳知识产权保护政策制定具有参考意义，或具备一定社会意义和影响。企业可以围绕案件背景、维权策略、证据组织、风险预警、团队协同和经验复盘来提炼亮点。",
        "申报时还需承诺，在不涉及商业秘密等敏感信息的前提下，同意将项目有关信息、研究成果、维权经验等向社会公开并供他人无偿使用。换句话说，优秀项目不仅能缓解企业成本压力，也可能成为行业样板，帮助更多深圳企业提升海外维权能力。",
        "同时要避开不予资助情形：不符合相关法律法规规章及专项资金管理要求的，不予资助；被依法依规纳入严重失信主体名单的，不予资助；已经获得市级同类资助或者奖励的，不予资助；申请人主体已经消亡或进入破产清算程序的，也不予资助。同一事项也不可与深圳市商标品牌指导站培育资助项目中开展商标维权服务的同类项目重复申报。",
        "建议企业立即开展三项准备：第一，建立费用台账，按项目归集合同、发票、付款凭证和服务成果；第二，整理法律文书链条，确认判决、裁决或和解协议的生效状态；第三，形成项目总结，说明维权难点、策略选择、产业价值和制度改进。材料越能体现真实性、必要性和示范性，越有利于呈现项目价值。",
        f"{hook}。对于已经完成海外知识产权维权项目的深圳企业而言，这项政策不只是资金补贴，更是一次把维权成果转化为品牌信用、合规能力和国际竞争力的机会。现在开始复盘项目、核验条件、准备证明材料，才能在申报窗口到来时更从容地把握政策红利。",
    ]
    if style_name == "清单速读型":
        angles[8] = "速读清单如下：看主体，是否深圳登记经营并有稳定办公场所；看制度，是否具备人员、合规、预警和风险防控机制；看结果，是否已有判决、仲裁裁决或和解协议且未载明申请人侵权；看时间，是否落在上三年度1月1日起至申请截止日止；看费用，是否扣除保险赔付款和和解费用；看重复，是否未获市级同类资助且未与同类商标维权服务重复申报。"
    if style_name == "流程指导型":
        angles[8] = "推荐按流程推进：先判断项目类型，排除美国“337”调查案件；再核验主体资格和信用状态；随后归集法律文书、费用凭证、合同发票和付款记录；接着撰写项目总结，突出维权能力提升和产业借鉴意义；最后检查是否存在市级同类资助、重复申报、主体消亡或破产清算等风险点。"
    if style_name == "成本减负型":
        angles[1] += " 对许多成长型出海企业来说，最高不超过200万元的支持，能够显著缓解跨境维权带来的现金流压力。"
    return angles


def build_ip_rights_article(company: CompanyProfile = DEFAULT_COMPANY_PROFILE) -> List[Article]:
    """生成 10 篇结合公司业务资料的知识产权海外维权资助宣传稿。"""
    articles: List[Article] = []
    for i, (title, style_name, hook) in enumerate(STYLES, start=1):
        body = "\n\n".join(_paragraphs(style_name, hook, i, company))
        articles.append(Article(i, title, style_name, body))
    return articles


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\s]+", "_", name).strip("_")
    return cleaned[:80]


def _doc_xml(article: Article) -> str:
    paras = [article.title, f"风格：{article.style}", *article.body.split("\n\n")]
    chunks = []
    for n, para in enumerate(paras):
        text = html.escape(para)
        style = '<w:pStyle w:val="Title"/>' if n == 0 else ''
        chunks.append(f'<w:p><w:pPr>{style}</w:pPr><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>')
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ''.join(chunks) + '<w:sectPr/></w:body></w:document>'


def write_docx(article: Article, path: Path) -> None:
    content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", _doc_xml(article))


def write_summary(articles: Iterable[Article], output_dir: Path, summary_path: Path) -> None:
    lines = [f"# {POLICY_NAME}推广文档汇总", "", f"生成日期：{date.today().isoformat()}", "", "| 序号 | 标题 | 风格 | 文件 |", "|---:|---|---|---|"]
    for article in articles:
        filename = f"{article.index:02d}_{_safe_filename(article.title)}.docx"
        lines.append(f"| {article.index} | {article.title} | {article.style} | {output_dir / filename} |")
    lines.extend(["", "## 政策要点", "", f"- 设定依据：{POLICY_RULES['basis']}。", f"- 资助标准：{POLICY_RULES['cap_per_project']} {POLICY_RULES['deductions']}", f"- 申报限制：{POLICY_RULES['annual_limit']} {POLICY_RULES['exclusion_337']}"])
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_articles_for_branch(branch: str = IP_RIGHTS_BRANCH, company: CompanyProfile = DEFAULT_COMPANY_PROFILE) -> List[Article]:
    """按业务分支生成文章，便于在原批量生成框架中增量扩展新政策。"""
    if branch != IP_RIGHTS_BRANCH:
        raise ValueError(f"不支持的业务分支：{branch}")
    return build_ip_rights_article(company)


def generate(output_dir: Path = DEFAULT_OUTPUT_DIR, summary_path: Path = DEFAULT_SUMMARY, company: CompanyProfile = DEFAULT_COMPANY_PROFILE) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    articles = build_articles_for_branch(IP_RIGHTS_BRANCH, company)
    paths = []
    for article in articles:
        path = output_dir / f"{article.index:02d}_{_safe_filename(article.title)}.docx"
        write_docx(article, path)
        paths.append(path)
    write_summary(articles, output_dir, summary_path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="批量生成知识产权海外维权资助推广 docx")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="docx 输出目录")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="Markdown 汇总文件")
    parser.add_argument("--company-name", default=DEFAULT_COMPANY_PROFILE.name, help="公司/主体名称，可用泛称")
    parser.add_argument("--industry", default=DEFAULT_COMPANY_PROFILE.industry, help="公司行业与业务方向")
    parser.add_argument("--products", default=DEFAULT_COMPANY_PROFILE.products, help="主要产品或服务")
    parser.add_argument("--markets", default=DEFAULT_COMPANY_PROFILE.overseas_markets, help="海外市场布局")
    parser.add_argument("--ip-assets", default=DEFAULT_COMPANY_PROFILE.ip_assets, help="知识产权资产")
    parser.add_argument("--rights-scenario", default=DEFAULT_COMPANY_PROFILE.rights_scenario, help="海外维权业务场景")
    parser.add_argument("--compliance-basis", default=DEFAULT_COMPANY_PROFILE.compliance_basis, help="知识产权管理制度基础")
    args = parser.parse_args()
    company = CompanyProfile(
        name=args.company_name,
        industry=args.industry,
        products=args.products,
        overseas_markets=args.markets,
        ip_assets=args.ip_assets,
        rights_scenario=args.rights_scenario,
        compliance_basis=args.compliance_basis,
    )
    paths = generate(args.output_dir, args.summary, company)
    print(f"生成 {len(paths)} 个 docx 文件，汇总：{args.summary}")


if __name__ == "__main__":
    main()
