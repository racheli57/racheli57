# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
import re

POLICY_TITLE = "深圳市工业和信息化局关于印发《深圳市工业和信息化局打造人工智能先锋城市项目扶持计划操作规程（2026年修订版）》的通知"
OUTPUT_DIR = Path.cwd()

ARTICLE_TITLE = "深圳AI企业关注：人工智能先锋城市扶持计划修订，最高资助3000万元"
ARTICLE_PARAGRAPHS = [
    "深圳市工业和信息化局正式印发《深圳市工业和信息化局打造人工智能先锋城市项目扶持计划操作规程（2026年修订版）》。本规程自2026年5月1日起施行，有效期至2027年6月30日，重点聚焦算力支撑、基础数据、人工智能软件、人工智能产品、人工智能服务等方向。对于正在布局大模型应用、智能制造升级、具身智能机器人和AI软件生态的深圳企业来说，这是一项值得尽早研究的重点政策。",
    "本次项目扶持计划下设十个类别，均采用事后奖补类支持方式，覆盖“模型券”、人工智能行业应用示范标杆、国家“揭榜挂帅”配套、国产人工智能生态源头创新中心、人工智能软件开源奖励、高端展会/论坛/大赛、具身智能机器人产品应用奖励，以及首版次软件、公共技术服务平台、软件名园等方向。企业应先判断业务与项目类别的匹配度，再倒排材料准备计划。",
    "模型券项目适合已经购买经备案生成式人工智能模型服务、开展智能体开发应用的企业。政策明确，单家企业每年申领模型券额度原则上不超过100万元，最高不超过200万元，可按不超过模型购买费用30%的比例抵扣；兑现时，项目应已完成模型服务或智能体开发应用，且购买人工智能模型服务总费用不低于50万元。合同、发票、支付凭证和验收材料应提前归档。",
    "人工智能行业应用示范标杆项目更适合具备实际落地场景的企业，支持AI+先进制造、AI+现代服务、AI+城市治理、AI+公共服务、AI for Science等方向。示范应用项目最高资助200万元，标杆应用项目最高资助1000万元，资助比例为经核定项目建设主体实际投入的30%。申报时不仅要准备财务票据，还要呈现技术创新、应用效果和复制推广价值。",
    "承担国家部委人工智能领域“揭榜挂帅”任务的单位，也可关注深圳配套支持：国家有资金支持的，可按1∶1给予最高1000万元配套；国家没有资金支持的，入围或优胜项目可按投入获得最高500万元或1000万元资助。国产人工智能生态源头创新中心项目面向全栈国产技术与模型迁移适配服务能力，单个创新中心每年获资助金额合计最高可达3000万元。",
    "具身智能机器人企业同样值得关注。政策提出，符合条件的申报产品按年度实际销售金额的5%给予单家企业最高300万元奖励。申报单位需具备较强研发实力和产品自主知识产权，上年度研发投入不少于1000万元；产品需满足首次销售、年度销售额、深圳设计或生产、检测认证等要求。",
    "深圳金赋科技有限公司长期深耕政策数据与企业政策服务，依托补贴数据平台累计收录1100万条全国四级政府公开政策数据，并通过补贴平台为企业提供政策匹配、资格评估、申报规划、材料编写指导、流程管控和合规审查等服务。面对本次人工智能先锋城市扶持计划，企业可先进行政策匹配诊断，再结合合同、发票、知识产权、研发投入、项目总结报告等材料建立申报台账。",
    "需要提醒的是，政策申报并不等同于简单提交材料。企业应核查是否在深圳市内实际经营、项目实施地和实施周期是否符合指南要求、是否存在同一建设内容多头申报、信用记录是否合规，以及费用是否与可资助范围一致。想了解企业是否符合本政策或其他深圳补贴申报条件，可使用深圳金赋旗下补贴平台，依托补贴数据平台的AI算法生成专属补贴推荐列表。",
]


def sanitize_windows_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip().rstrip('.')
    return cleaned[:180] or "policy_article"


def paragraph_xml(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{style_xml}<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"


def create_docx(path: Path, title: str, paragraphs: list[str]) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    word_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="SimSun" w:eastAsia="SimSun"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:rFonts w:ascii="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:sz w:val="32"/></w:rPr></w:style></w:styles>"""
    body = paragraph_xml(title, "Title") + "".join(paragraph_xml(p) for p in paragraphs)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/_rels/document.xml.rels", word_rels)
        docx.writestr("word/styles.xml", styles)
        docx.writestr("word/document.xml", document)


def main() -> None:
    output_name = sanitize_windows_filename(POLICY_TITLE) + ".docx"
    output_path = OUTPUT_DIR / output_name
    create_docx(output_path, ARTICLE_TITLE, ARTICLE_PARAGRAPHS)
    article_markdown = "\n\n".join([f"# {ARTICLE_TITLE}", *ARTICLE_PARAGRAPHS])
    Path("generated_documents.md").write_text(
        "# 生成的Word文档列表\n\n"
        f"- `{output_name}`\n\n"
        "## 文章主题\n\n"
        f"- {ARTICLE_TITLE}\n"
        "- 政策来源：深圳市工业和信息化局\n"
        "- 政策有效期：2026年5月1日至2027年6月30日\n"
        "- 重点内容：模型券、示范标杆、揭榜挂帅配套、国产人工智能生态源头创新中心、开源奖励、展会/论坛/大赛、具身智能机器人奖励等。\n\n"
        "## 推广文章内容\n\n"
        f"{article_markdown}\n",
        encoding="utf-8",
    )
    print(output_path)

if __name__ == "__main__":
    main()
